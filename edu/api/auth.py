# lms-extension-backend/edu/api/auth.py

import random
import string
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken  # Импортируем для создания токенов

from ..models import User, Verification
from ..schema.auth import RegistrationSchema, LoginSchema, VerificationSchema
from ..schema import Message

# Этот роутер будет публичным, так как мы указали auth=None при его регистрации
router = Router()


@router.post("register/", response={200: Message, 400: Message})
def register(request, payload: RegistrationSchema):
    if not payload.email.endswith("@edu.centraluniversity.ru"):
        raise HttpError(
            400, "Only @edu.centraluniversity.ru emails are allowed"
        )

    if User.objects.filter(email=payload.email).exists():
        return 400, Message(message="Email already registered")

    user = User.objects.create_user(
        email=payload.email, password=payload.password, is_active=False
    )

    code = "".join(random.choices(string.digits, k=6))
    Verification.objects.create(user=user, code=code)

    try:
        send_mail(
            "Добро пожаловать на коммунистический сервер",
            f"На входе просят пароль, вот он: {code}",
            None,
            [payload.email],
            fail_silently=False,
        )
    except Exception as e:
        # В реальном приложении здесь лучше логировать ошибку
        # Для отладки можно временно вернуть ошибку
        user.delete()  # Откатываем создание пользователя, если письмо не ушло
        return 400, Message(message=f"Could not send email. Error: {e}")

    return 200, Message(message="Verification code sent to your email")


@router.post("verify/", response={200: Message})
def verify_email(request, payload: VerificationSchema):
    user = get_object_or_404(User, email=payload.email)
    verification = get_object_or_404(
        Verification, user=user, code=payload.code
    )

    user.is_active = True
    user.save()
    verification.delete()

    return Message(message="Email verified successfully")


@router.post("login/")
def login(request, payload: LoginSchema):
    user = authenticate(email=payload.email, password=payload.password)
    if user is not None:
        if user.is_active:
            # Если пользователь существует и активен, генерируем для него токены
            refresh = RefreshToken.for_user(user)
            return {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        else:
            # Пользователь есть, но не подтвердил почту
            raise HttpError(403, "Email not verified")
    else:
        raise HttpError(401, "Invalid credentials or email not verified")
