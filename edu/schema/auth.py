# edu/schema/auth.py

from ninja import Schema


class RegistrationSchema(Schema):
    email: str
    password: str


class VerificationSchema(Schema):
    email: str
    code: str


class LoginSchema(Schema):
    email: str
    password: str