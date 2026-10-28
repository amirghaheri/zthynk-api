from fastapi import FastAPI
from app.routes.businesses import router as business_router
from app.routes.users import router as user_router
from app.routes.auth import router as auth_router
from app.routes.services import router as service_router
from app.routes.business_services import router as business_services_router

app = FastAPI(
    title="ZTHYNK API",
    description="AI-powered growth platform for local businesses",
    version="0.1.0",
)


app.include_router(business_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(service_router)
app.include_router(business_services_router)


@app.get("/")
async def root():
    return {
        "name": "ZTHYNK",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "service": "ZTHYNK API",
        "status": "ok",
    }
