from fastapi import FastAPI
from auth import router

app = FastAPI()

app.include_router(router, prefix="/auth")

@app.get("/")
async def root():
    return {"message": "Hello, World!"}