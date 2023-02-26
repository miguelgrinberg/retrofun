from fastapi import FastAPI
from .router import router

app = FastAPI()
app.include_router(router)
