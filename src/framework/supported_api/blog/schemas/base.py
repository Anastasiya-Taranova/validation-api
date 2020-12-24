from typing import Dict
from typing import List
from typing import Optional
from typing import Text
from typing import Union

from pydantic import BaseModel


class TestRequest(BaseModel):
    url: str


class JsonApiObject(BaseModel):
    errors: Optional[List[Text]] = None
    data: Optional[Union[Dict, List]]


class TestRequestApi(JsonApiObject):
    data: TestRequest
