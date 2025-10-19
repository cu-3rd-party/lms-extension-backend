# edu/api/auth.py

import random
import string
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from ..models import User, Verification
from ..schema.auth import RegistrationSchema, LoginSchema, VerificationSchema

router = Router()


@router.post("register/")
def register(request, payload: RegistrationSchema):
    if not payload.email.endswith("@edu.centraluniversity.ru"):
        raise HttpError(
            400, "Only @edu.centraluniversity.ru emails are allowed"
        )

    if User.objects.filter(email=payload.email).exists():
        raise HttpError(400, "Email already registered")

    user = User.objects.create_user(
        email=payload.email, password=payload.password, is_active=False
    )

    code = "".join(random.choices(string.digits, k=6))
    Verification.objects.create(user=user, code=code)

    send_mail(
        "Добро пожаловать на коммунистический сервер",
        f"На входе просят пароль, вот он: {code}",
        None,
        [payload.email],
        fail_silently=False,
    )

    return {"message": "Verification code sent to your email"}


@router.post("verify/")
def verify_email(request, payload: VerificationSchema):
    user = get_object_or_404(User, email=payload.email)
    verification = get_object_or_404(
        Verification, user=user, code=payload.code
    )

    user.is_active = True
    user.save()
    verification.delete()

    return {"message": "Email verified successfully"}


@router.post("login/")
def login(request, payload: LoginSchema):
    user = authenticate(email=payload.email, password=payload.password)
    if user is not None and user.is_active:
        # Здесь вы можете реализовать систему токенов, например, JWT
        return {"message": "Login successful"}
    else:
        raise HttpError(401, "Invalid credentials or email not verified")
