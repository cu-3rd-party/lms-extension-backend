from ninja import Schema


class Message(Schema):
    message: str


class BaseFile(Schema):
    # filename теперь обязательное поле, чтобы клиент знал, что это за файл
    filename: str
    contents: str # (base64 encoded)


class FileMessage(Message, BaseFile): ...