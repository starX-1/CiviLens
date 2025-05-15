from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import queries
from core.config import settings

app = FastAPI(
    title="CivicLens API",
    description="AI-Powered Political Literacy & Policy Explainer",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(queries.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to CivicLens API - Enhancing political literacy"}