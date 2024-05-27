from fastapi import FastAPI
from auth import router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/auth")

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
