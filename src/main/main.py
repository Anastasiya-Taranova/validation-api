import logging
import os
import traceback
from typing import Dict, List, Optional, Text, Union

import requests
import uvicorn
import validators
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Form
from pydantic import BaseModel
from starlette.testclient import TestClient

app = FastAPI()
client = TestClient(app)
templates = Jinja2Templates(directory="jinja2")
API_TIMEOUT = 2


class User(BaseModel):
    id: int


AllUsersT = List[User]


class Post(BaseModel):
    content: str
    author_id: int
    id: Optional[int] = None


AllPostsT = List[Post]


class TestRequest(BaseModel):
    url: str


class JsonApiObject(BaseModel):
    errors: Optional[List[Text]] = None
    data: Optional[Union[Dict, List]]


class RunTestRequest(JsonApiObject):
    data: TestRequest


class AllUsersResponse(JsonApiObject):
    data: AllUsersT


class AllPostsResponse(JsonApiObject):
    data: AllPostsT


class SinglePostResponse(JsonApiObject):
    data: Post


def mute_root_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.CRITICAL)
    for _handler in root_logger.handlers:
        root_logger.removeHandler(_handler)


def configure_logging(logger_name: str) -> logging.Logger:
    debug = 1
    if isinstance(debug, str) and debug.isdigit():
        debug = int(debug)

    LEVELS = {
        True: logging.DEBUG,
        False: logging.WARNING,
    }

    FORMATS = {
        0: "{asctime} | {name}.{levelname} | {module}.{funcName} | {message}",
        1: "{asctime} | {name}.{levelname}\n| {pathname}:{lineno}\n| {message}\n",
    }

    lvl = LEVELS[debug]
    fmt = FORMATS[debug]

    mute_root_logger()

    logger = logging.getLogger(logger_name)
    logger.setLevel(lvl)

    handler = logging.StreamHandler()
    handler.setLevel(lvl)

    formatter = logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S", style="{")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = configure_logging("main")


@app.get("/", response_class=HTMLResponse)
async def view_index(request: Request):
    logger.debug(request)
    return templates.TemplateResponse('index.html', context={"request": request})


@app.post("/")
async def view_test(req: RunTestRequest) -> JsonApiObject:
    logger.debug(req)
    test_api_server = req.data.url

    resp = JsonApiObject()

    try:
        test_post_global(test_api_server)
    except AssertionError as err:
        resp.data = {"ok": False, "description": str(err)}
    except (requests.Timeout, requests.ConnectionError):
        resp.data = {"ok": False, "description": "your api is down"}
    except Exception as err:
        tb = traceback.format_exc()
        resp.errors = ["our server fault", str(err), tb]
    else:
        resp.data = {"ok": True, "description": "hemos pasado"}

    return resp


def validate_url(server) -> None:
    assert validators.url(server), f"url {server} is not valid"


def test_post_global(test_api_server):
    validate_url(test_api_server)
    authors = get_authors(test_api_server)
    # TODO: validate that authors != []
    author = authors[0]

    post_params = generate_post_params(author)
    new_post = create_new_post(test_api_server, post_params)
    validate_post(new_post, post_params)

    posts = get_all_posts(test_api_server)
    validate_post_in_posts(new_post, posts)

    existing_post = get_post_by_id(test_api_server, new_post.id)
    validate_post(existing_post, new_post)


def get_post_by_id(server: Text, new_post: int) -> Post:
    url = f"{server}/api/v1/blog/post/{new_post}"
    response = requests.get(url, timeout=API_TIMEOUT)
    assert response.status_code == 200, f"{url} does not work: {response.status_code}"
    payload = response.json()
    posts_resp = SinglePostResponse.parse_obj(payload)
    return posts_resp.data


def generate_post_params(author: User) -> Dict:
    post = Post(author_id=author.id, content=os.urandom(8).hex())
    params = {
        key: value
        for key, value in post.dict().items()
        if value
    }
    return params


def get_all_posts(server: Text) -> AllPostsT:
    url = f"{server}/api/v1/blog/post/"
    response = requests.get(url, timeout=API_TIMEOUT)
    assert response.status_code == 200, f"{url} does not work: {response.status_code}"
    payload = response.json()
    posts_resp = AllPostsResponse.parse_obj(payload)
    posts = posts_resp.data
    return posts


def validate_post_in_posts(new_post: Post, posts: AllPostsT) -> None:
    assert new_post in posts


def get_authors(server: Text) -> AllUsersT:
    url = f"{server}/api/v1/user/"
    response = requests.get(url, timeout=API_TIMEOUT)
    assert response.status_code == 200, f"{url} does not work: {response.status_code}"
    payload = response.json()
    users_resp = AllUsersResponse.parse_obj(payload)
    users = users_resp.data
    return users


def validate_post(post: Post, post_params: Union[Dict, Post]) -> None:
    post_params = post_params.dict() if isinstance(post_params, Post) else post_params
    assert "id" in post, f"post {post} does not have a key 'id'"
    assert isinstance(post.id, int), f"post object must have an integer id, got {post.id} instead"
    for attr_name, expected_value in post_params.items():
        existing_value = getattr(post, attr_name)
        assert \
            existing_value == expected_value, \
            f"post.{attr_name} == {existing_value!r}, while expected {existing_value!r}"


def create_new_post(server: Text, new_post_params: Dict) -> Post:
    url = f"{server}/api/v1/blog/post/"
    response = requests.post(url, json=new_post_params, timeout=API_TIMEOUT)
    assert response.status_code == 201, f"{url} does not work: {response.status_code}"
    api_response_json = response.json()
    api_response = SinglePostResponse.parse_obj(api_response_json)
    post = api_response.data
    return post


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7080)
