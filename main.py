from fastapi import FastAPI
from routes.orders import router as order_router

app = FastAPI(
    title="Dabbewala",
    description="Dabbewala API",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# register routers
app.include_router(order_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
