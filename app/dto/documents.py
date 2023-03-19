from fastapi import UploadFile

from app.v1.schemas.base import BaseModelORM


class UpdateDocumentDTO(BaseModelORM):
    file_name: str
    size_bytes: int
    mime_type: str


class SystemFileDTO:
    def __init__(
        self,
        file_name: str,
        file: UploadFile,
    ):
        self.file_name = file_name
        self.file = file

