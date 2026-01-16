from typing import Optional

from pydantic import BaseModel


class UserDTO(BaseModel):
    client_id: str = ""
    crm_url: str = ""
    crm_api_key: str = ""
    module_name: str = ""
    module_code: str = ""
    active: Optional[bool] = False
    freeze: Optional[bool] = False
