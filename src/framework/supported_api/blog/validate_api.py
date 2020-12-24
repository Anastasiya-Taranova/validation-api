import os
from typing import Dict
from typing import Text
from typing import Union

import requests
import validators

from framework.supported_api.blog.schemas.posts import Post
from framework.supported_api.blog.schemas.posts import PostApi
from framework.supported_api.blog.schemas.posts import PostList
from framework.supported_api.blog.schemas.posts import PostListApi
from framework.supported_api.blog.schemas.users import User
from framework.supported_api.blog.schemas.users import UserList
from framework.supported_api.blog.schemas.users import UserListApi

API_TIMEOUT = 2


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
    posts_resp = PostApi.parse_obj(payload)
    return posts_resp.data


def generate_post_params(author: User) -> Dict:
    post = Post(author_id=author.id, content=os.urandom(8).hex())
    params = {key: value for key, value in post.dict().items() if value}
    return params


def get_all_posts(server: Text) -> PostList:
    url = f"{server}/api/v1/blog/post/"
    response = requests.get(url, timeout=API_TIMEOUT)
    assert response.status_code == 200, f"{url} does not work: {response.status_code}"
    payload = response.json()
    posts_resp = PostListApi.parse_obj(payload)
    posts = posts_resp.data
    return posts


def validate_post_in_posts(new_post: Post, posts: PostList) -> None:
    assert new_post in posts


def get_authors(server: Text) -> UserList:
    url = f"{server}/api/v1/user/"
    response = requests.get(url, timeout=API_TIMEOUT)
    assert response.status_code == 200, f"{url} does not work: {response.status_code}"
    payload = response.json()
    users_resp = UserListApi.parse_obj(payload)
    users = users_resp.data
    return users


def validate_post(post: Post, post_params: Union[Dict, Post]) -> None:
    post_params = post_params.dict() if isinstance(post_params, Post) else post_params

    assert isinstance(
        post.id, int
    ), f"post object must have an integer id, got {post.id!r} instead"

    for attr_name, expected_value in post_params.items():
        existing_value = getattr(post, attr_name)
        assert (
            existing_value == expected_value
        ), f"post.{attr_name} == {existing_value!r}, while expected {existing_value!r}"


def create_new_post(server: Text, new_post_params: Dict) -> Post:
    url = f"{server}/api/v1/blog/post/"
    request = PostApi(data=Post.parse_obj(new_post_params))
    response = requests.post(url, json=request.dict(), timeout=API_TIMEOUT)
    assert response.status_code == 201, f"{url} does not work: {response.status_code}"
    api_response_json = response.json()
    api_response = PostApi.parse_obj(api_response_json)
    post = api_response.data
    return post


def validate_url(server) -> None:
    assert validators.url(server), f"url {server} is not valid"
