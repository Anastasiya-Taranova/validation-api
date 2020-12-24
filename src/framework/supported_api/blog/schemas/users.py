from typing import List

from pydantic import BaseModel

from framework.supported_api.blog.schemas.base import JsonApiObject


class User(BaseModel):
    id: int


UserList = List[User]


class UserListApi(JsonApiObject):
    data: UserList
