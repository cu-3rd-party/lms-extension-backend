from ninja import Schema


class Message(Schema):
    message: str


class BaseFile(Schema):
    filename: str | None = None
    contents: str


class FileMessage(Message, BaseFile):
    ...
