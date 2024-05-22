from fastapi.routing import APIRouter
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import os

router = APIRouter()


templates = Jinja2Templates(directory="python/src/FastAPI/templates")


@router.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = "python/src/FastAPI/templates/index.html"
    with open(html_path, 'r') as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


@router.get("/admin/sign_in", response_class=HTMLResponse)
async def admin_sign_in():
    html_path = "python/src/FastAPI/templates/admin_sign_in.html"
    with open(html_path, 'r') as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


@router.post("/admin/sign_in", response_class=HTMLResponse)
async def handle_admin_sign_in(request: Request, login: str = Form(...), password: str = Form(...)):

    if login == "admin" and password == "password":
        return templates.TemplateResponse("admin_page.html", {"request": request})
    else:
        return templates.TemplateResponse("admin_sign_in.html", {"request": request, "error": "Invalid credentials"})