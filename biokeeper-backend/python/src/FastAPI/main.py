from fastapi import Depends, FastAPI

from routers.users import router as users_router
from routers.researches import router as researches_router
from routers.kits import router as kit_router
from routers.samples import router as samples_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

app = FastAPI(docs_url=None, redoc_url=None, openapi_url = None)

from routers.docs import get_current_username, get_swagger_ui_html, get_openapi

@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title = "FastAPI", version="0.1.0", routes=app.routes)

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







if __name__ == "__main__":
    import asyncio
    from mq import start_consuming
    
    from threading import Thread
    def start_consumer_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_consuming())
    loop = asyncio.new_event_loop()
    t = Thread(target=start_consumer_loop, args=(loop,))
    t.start()
    # asyncio.run(start_consuming())
    
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=1337, reload=True)
