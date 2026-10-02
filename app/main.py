from fastapi import FastAPI
from app.api.routes import api_router

app = FastAPI(
    title="CareBook API",
    description="Diagnostic test booking and simulated payment service",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
