
from fastapi import FastAPI
from users import router as users_router
from researches import router as researches_router
from kits import router as kit_router
from samples import router as samples_router

app = FastAPI()
app.include_router(users_router)
app.include_router(researches_router)
app.include_router(kit_router)
app.include_router(samples_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}



# @app.get("/")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)