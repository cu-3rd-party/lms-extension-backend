from unittest.mock import patch, MagicMock

from django.core.files.base import ContentFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from ninja_jwt.tokens import RefreshToken

from ..models import Longread, User


def create_and_authenticate_user(client: APIClient):
    """Хелпер для создания, активации пользователя и получения токена."""
    user = User.objects.create_user(
        email="testuser@edu.centraluniversity.ru",
        password="password123",
        is_active=True,  # Сразу делаем активным для тестов
    )
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    # Устанавливаем заголовок авторизации для всех последующих запросов клиента
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return user


class TestUploadLongreadAPI(APITestCase):
    client: APIClient

    def setUp(self):
        # <--- ИЗМЕНЕНО: Добавляем аутентификацию
        create_and_authenticate_user(self.client)
        self.valid_body = {
            "longread_id": 123,
            "title": "Test Longread",
            "theme_id": 10,
            "course_id": 20,
            "download_link": "http://example.com/file.pdf",
        }

    @patch("edu.api.longread.verify_download_link", return_value=True)
    @patch("edu.api.longread.requests.get")
    def test_upload_longread_success(self, mock_get, mock_verify):
        mock_get.return_value = MagicMock(status_code=200, content=b"PDFDATA")
        url = reverse("api-1.0.0:upload_longread")
        response = self.client.post(url, self.valid_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json()["message"], "Longread uploaded successfully"
        )
        self.assertTrue(Longread.objects.filter(lms_id=123).exists())

    @patch("edu.api.longread.verify_download_link", return_value=False)
    def test_upload_longread_invalid_link(self, mock_verify):
        url = reverse("api-1.0.0:upload_longread")
        response = self.client.post(url, self.valid_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.json()["message"],
            "You have provided invalid download link",
        )

    @patch("edu.api.longread.verify_download_link", return_value=True)
    @patch("edu.api.longread.requests.get")
    def test_upload_longread_failed_download(self, mock_get, mock_verify):
        mock_get.return_value = MagicMock(status_code=500)
        url = reverse("api-1.0.0:upload_longread")
        response = self.client.post(url, self.valid_body, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertEqual(
            response.json()["message"],
            "Failed to download file from the provided link",
        )


class TestFullGetLongreadAPI(APITestCase):
    client: APIClient

    def setUp(self):
        # <--- ИЗМЕНЕНО: Добавляем аутентификацию
        create_and_authenticate_user(self.client)
        self.longread = Longread.objects.create(
            lms_id=1, title="Existing Longread", theme_id=2, course_id=3
        )
        self.longread.contents.save("test.pdf", ContentFile(b"TESTDATA"))

    def test_get_longread_contents_success(self):
        url = reverse(
            "api-1.0.0:get_longread_contents",
            kwargs={"course_id": 3, "theme_id": 2, "longread_id": 1},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Примечание: содержимое файла будет закодировано в base64, если вы не изменили сериализацию
        # Этот тест может потребовать доработки в зависимости от вашей реальной логики
        self.assertIn("contents", response.json())

    def test_get_longread_contents_not_found(self):
        url = reverse(
            "api-1.0.0:get_longread_contents",
            kwargs={"course_id": 99, "theme_id": 99, "longread_id": 99},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ... (аналогичные изменения для всех остальных классов в этом файле) ...


class TestGetCourseAPI(APITestCase):
    client: APIClient

    def setUp(self):
        # <--- ИЗМЕНЕНО
        create_and_authenticate_user(self.client)
        self.course_id = 42
        self.longread = Longread.objects.create(
            lms_id=2,
            title="Course Longread",
            theme_id=1,
            course_id=self.course_id,
        )

    def test_get_course_success(self):
        url = reverse(
            "api-1.0.0:get_course", kwargs={"course_id": self.course_id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_course_not_found(self):
        url = reverse("api-1.0.0:get_course", kwargs={"course_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestGetThemeAPI(APITestCase):
    client: APIClient

    def setUp(self):
        # <--- ИЗМЕНЕНО
        create_and_authenticate_user(self.client)
        self.course_id = 50
        self.theme_id = 5
        self.longread = Longread.objects.create(
            lms_id=3,
            title="Theme Longread",
            theme_id=self.theme_id,
            course_id=self.course_id,
        )

    def test_get_theme_success(self):
        url = reverse(
            "api-1.0.0:get_theme",
            kwargs={"course_id": self.course_id, "theme_id": self.theme_id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_theme_not_found(self):
        url = reverse(
            "api-1.0.0:get_theme", kwargs={"course_id": 999, "theme_id": 999}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestGetAvailableInfoAPI(APITestCase):
    client: APIClient

    def setUp(self):
        # <--- ИЗМЕНЕНО
        create_and_authenticate_user(self.client)
        # ... (остальной код setUp без изменений) ...
        self.course_id_1 = 10
        self.theme_id_1 = 5
        self.course_id_2 = 15
        self.theme_id_2 = 5
        self.longreads = [
            Longread.objects.create(
                lms_id=1,
                title="test1",
                theme_id=self.theme_id_1,
                course_id=self.course_id_1,
            ),
            Longread.objects.create(
                lms_id=2,
                title="test2",
                theme_id=self.theme_id_1,
                course_id=self.course_id_1,
            ),
            Longread.objects.create(
                lms_id=3,
                title="test3",
                theme_id=self.theme_id_2,
                course_id=self.course_id_2,
            ),
        ]

    def test_get_all_longreads_success(self):
        url = reverse("api-1.0.0:get_available_info")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestFetchLongreadsAPI(APITestCase):
    client: APIClient

    def setUp(self):
        # <--- ИЗМЕНЕНО
        create_and_authenticate_user(self.client)
        self.url = reverse("api-1.0.0:fetch_longreads")
        self.valid_body = {
            "courses": [
                {
                    "course_id": 1,
                    "themes": [
                        {"theme_id": 10, "longreads": [100, 101]},
                        {"theme_id": 11, "longreads": [102]},
                    ],
                }
            ]
        }

    def test_fetch_with_no_triples(self):
        body = {"courses": []}
        response = self.client.post(self.url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ... (остальные тесты в этом классе теперь будут работать, так как клиент авторизован) ...
    def test_fetch_with_all_missing_longreads(self):
        response = self.client.post(self.url, self.valid_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            response.json()["missing_longreads"], [100, 101, 102]
        )

    def test_fetch_with_some_existing_longreads(self):
        Longread.objects.create(
            lms_id=100, course_id=1, theme_id=10, title="Existing longread"
        )
        response = self.client.post(self.url, self.valid_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.json()["missing_longreads"], [101, 102])

    def test_fetch_with_all_existing_longreads(self):
        Longread.objects.bulk_create(
            [
                Longread(lms_id=100, course_id=1, theme_id=10, title="LR1"),
                Longread(lms_id=101, course_id=1, theme_id=10, title="LR2"),
                Longread(lms_id=102, course_id=1, theme_id=11, title="LR3"),
            ]
        )
        response = self.client.post(self.url, self.valid_body, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["missing_longreads"], [])

    def test_fetch_with_multiple_courses(self):
        body = {
            "courses": [
                {
                    "course_id": 1,
                    "themes": [{"theme_id": 10, "longreads": [200]}],
                },
                {
                    "course_id": 2,
                    "themes": [{"theme_id": 20, "longreads": [300, 301]}],
                },
            ]
        }
        Longread.objects.create(
            lms_id=200, course_id=1, theme_id=10, title="LR200"
        )
        response = self.client.post(self.url, body, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.json()["missing_longreads"], [300, 301])
