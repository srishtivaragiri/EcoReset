from pydantic import BaseModel
from typing import List

class CertRequest(BaseModel):
    file_list: List[str]
    file_hash: str
    device_path: str

class VerifyRequest(BaseModel):
    cert_id: str
    signature: str
    file_hash: str