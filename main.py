from fastapi import FastAPI
from routes.orders import router as order_router
from contextlib import asynccontextmanager
from database import create_tables


@asynccontextmanager
async def lifespan(app):
    create_tables()
    print("Tables created")
    yield
    print("Shutting down")


app = FastAPI(
    title="Dabbewala",
    description="Dabbewala API",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# register routers
app.include_router(order_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
