from fastapi import FastAPI
from routers.ratings import router as ratings_router

app = FastAPI()

app.include_router(ratings_router)
