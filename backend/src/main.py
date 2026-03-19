from fastapi import FastAPI
from routers.orders_router import router as ratings_router

app = FastAPI()

app.include_router(ratings_router)
