import asyncio
from fastapi import FastAPI
from .core.logging_config import configure_logging
from .api.routes import health, autocomplete
from fastapi.middleware.cors import CORSMiddleware
from .services.autocomplete_service import AutocompleteService

configure_logging()

app = FastAPI(
    title="Legal Autocomplete Service",
    version="0.1.0",
    description="A standalone intelligent autocomplete microservice."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(autocomplete.router, prefix="/api/v1", tags=["Autocomplete"])

@app.on_event("startup")
async def startup_event():
    svc = AutocompleteService()
    asyncio.create_task(svc.warmup())

@app.get("/", tags=["root"])
async def read_root():
    return {"message": f"Legal Autocomplete Service is running"}
