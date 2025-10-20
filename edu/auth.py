from ninja.security import HttpBearer
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import Token


# Мы используем JWTAuth из ninja_jwt для удобства,
# но переопределяем метод authenticate, чтобы добавить проверку is_active
class ActiveUserAuth(JWTAuth):
    def authenticate(self, request, token):
        # Стандартная аутентификация из библиотеки
        user = super().authenticate(request, token)
        # Наша дополнительная проверка: пользователь должен быть активен
        if user and user.is_active:
            return user
        return None
