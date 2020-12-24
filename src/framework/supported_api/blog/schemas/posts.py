from typing import List
from typing import Optional

from pydantic import BaseModel

from framework.supported_api.blog.schemas.base import JsonApiObject


class Post(BaseModel):
    content: str
    author_id: int
    id: Optional[int] = None


PostList = List[Post]


class PostListApi(JsonApiObject):
    data: PostList


class PostApi(JsonApiObject):
    data: Post
