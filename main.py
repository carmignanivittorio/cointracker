from fastapi import FastAPI

from fastapi_schemas import Pong

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/ping", response_model=Pong)
def ping() -> Pong:
    return Pong()
