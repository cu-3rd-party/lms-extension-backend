# edu/tests/test_auth.py

from unittest.mock import patch
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

from ..models import User, Verification, Longread


class AuthAPITestCase(APITestCase):
    client: APIClient

    def setUp(self):
        """Настройка тестовых данных и URL."""
        self.client = APIClient()
        self.user_data = {
            "email": "testuser@edu.centraluniversity.ru",
            "password": "veryStrongPassword123",
        }
        # Используем reverse для получения URL, чтобы тесты не ломались при их изменении
        # Обратите внимание, что ninja-router'у нужно указать версию api: api-1.0.0
        self.register_url = reverse("api-1.0.0:register")
        self.verify_url = reverse("api-1.0.0:verify_email")
        self.login_url = reverse("api-1.0.0:login")

    @patch("edu.api.auth.send_mail")  # Мокаем отправку email
    def test_registration_success(self, mock_send_mail):
        """Тест успешной регистрации нового пользователя."""
        response = self.client.post(self.register_url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "Verification code sent to your email")

        # Проверяем, что пользователь создан в БД, но не активен
        self.assertTrue(User.objects.filter(email=self.user_data["email"]).exists())
        user = User.objects.get(email=self.user_data["email"])
        self.assertFalse(user.is_active)

        # Проверяем, что для него создан код верификации
        self.assertTrue(Verification.objects.filter(user=user).exists())

        # Проверяем, что функция отправки письма была вызвана
        mock_send_mail.assert_called_once()

    def test_registration_fails_if_email_exists(self):
        """Тест: регистрация не удастся, если email уже занят."""
        # Сначала создаем пользователя
        User.objects.create_user(**self.user_data)
        # Пытаемся зарегистрировать его еще раз
        response = self.client.post(self.register_url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["message"], "Email already registered")

    def test_registration_fails_for_invalid_domain(self):
        """Тест: регистрация не удастся, если домен почты неверный."""
        invalid_data = {"email": "test@gmail.com", "password": "123"}
        response = self.client.post(self.register_url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["message"], "Only @edu.centraluniversity.ru emails are allowed")

    @patch("edu.api.auth.send_mail")
    def test_verification_success(self, mock_send_mail):
        """Тест успешной верификации пользователя."""
        # 1. Регистрируем пользователя
        self.client.post(self.register_url, self.user_data, format="json")
        user = User.objects.get(email=self.user_data["email"])
        code = Verification.objects.get(user=user).code

        # 2. Верифицируем с правильным кодом
        verification_data = {"email": self.user_data["email"], "code": code}
        response = self.client.post(self.verify_url, verification_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["message"], "Email verified successfully")

        # Проверяем, что пользователь стал активным
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        # Проверяем, что код верификации удален
        self.assertFalse(Verification.objects.filter(user=user).exists())

    def test_verification_fails_with_invalid_code(self):
        """Тест: верификация не удастся с неверным кодом."""
        User.objects.create_user(**self.user_data)
        verification_data = {"email": self.user_data["email"], "code": "000000"}
        response = self.client.post(self.verify_url, verification_data, format="json")
        
        # get_object_or_404 вернет 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_success_for_active_user(self):
        """Тест успешного входа для активного пользователя."""
        # Создаем активного пользователя
        user = User.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()

        response = self.client.post(self.login_url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)

    def test_login_fails_for_inactive_user(self):
        """Тест: вход не удастся для неактивного пользователя."""
        User.objects.create_user(**self.user_data) # is_active по умолчанию False
        response = self.client.post(self.login_url, self.user_data, format="json")

        # <--- ИЗМЕНЕНО: Ожидаем 401, а не 403
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # <--- ИЗМЕНЕНО: Проверяем правильное сообщение об ошибке
        self.assertEqual(response.json()["detail"], "Invalid credentials")

    def test_login_fails_with_wrong_password(self):
        """Тест: вход не удастся с неверным паролем."""
        user = User.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()

        wrong_credentials = {"email": self.user_data["email"], "password": "wrongpassword"}
        response = self.client.post(self.login_url, wrong_credentials, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["detail"], "Invalid credentials")

    def test_access_protected_endpoint_with_valid_token(self):
        """Тест: доступ к защищенному эндпоинту с валидным токеном."""
        # 1. Создаем активного пользователя
        user = User.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()

        # 2. Логинимся, чтобы получить токен
        login_response = self.client.post(self.login_url, self.user_data, format="json")
        access_token = login_response.json()["access"]

        # 3. Создаем данные, которые будет запрашивать защищенный эндпоинт
        Longread.objects.create(lms_id=1, title="Test", theme_id=2, course_id=3)
        protected_url = reverse("api-1.0.0:get_course", kwargs={"course_id": 3})

        # 4. Делаем запрос с токеном
        auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}
        response = self.client.get(protected_url, **auth_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)

    def test_access_protected_endpoint_without_token(self):
        """Тест: доступ к защищенному эндпоинту без токена запрещен."""
        protected_url = reverse("api-1.0.0:get_course", kwargs={"course_id": 3})
        response = self.client.get(protected_url)

        # ninja-jwt вернет 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)