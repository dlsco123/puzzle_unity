from fastapi import FastAPI
from routers import main_routes

app = FastAPI()

app.include_router(main_routes.router, prefix='/main', tags=['main'])