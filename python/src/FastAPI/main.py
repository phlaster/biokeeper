import os
from fastapi import FastAPI
from users import router as users_router
from researches import router as researches_router
from kits import router as kit_router
from samples import router as samples_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(researches_router)
app.include_router(kit_router)
app.include_router(samples_router)



# Mount the static files directory
app.mount("/static", StaticFiles(directory="python/src/FastAPI/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = "python/src/FastAPI/templates/index.html"
    with open(html_path, 'r') as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


@app.get("/admin/sign_in", response_class=HTMLResponse)
async def admin_sign_in():
    html_path = "python/src/FastAPI/templates/admin_sign_in.html"
    with open(html_path, 'r') as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=1337, reload=True)
