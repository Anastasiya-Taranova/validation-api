import traceback

import requests
import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.testclient import TestClient

from framework import dirs
from framework.supported_api.blog.schemas.base import JsonApiObject
from framework.supported_api.blog.schemas.base import TestRequestApi
from framework.supported_api.blog.validate_api import test_post_global
from framework.utils.logging import configure_logging

app = FastAPI()
client = TestClient(app)
templates = Jinja2Templates(directory=dirs.DIR_TEMPLATES)

LOGGER = configure_logging("main")


@app.get("/", response_class=HTMLResponse)
async def view_index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.post("/")
async def view_test(
    req: TestRequestApi,
) -> JsonApiObject:  # TODO: use a specific API obj
    LOGGER.debug(req)
    test_api_server = req.data.url

    resp = JsonApiObject()

    try:
        test_post_global(test_api_server)
    except AssertionError as err:
        tb = traceback.format_exc().split("\n")
        resp.data = {"ok": False, "description": str(err), "tb": tb}
    except (requests.Timeout, requests.ConnectionError):
        tb = traceback.format_exc().split("\n")
        resp.data = {"ok": False, "description": "your api is down", "tb": tb}
    except Exception as err:
        tb = traceback.format_exc()
        resp.errors = ["our server fault", str(err), tb]
    else:
        resp.data = {"ok": True, "description": "hemos pasado", "tb": None}

    return resp


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7080)
