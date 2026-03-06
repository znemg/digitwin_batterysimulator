from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import runs, network, ai

app = FastAPI(
    title="Digital Twin API",
    description="Backend for Digital Twin simulation analysis platform",
    version="1.0.0",
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(runs.router)
app.include_router(network.router)
app.include_router(ai.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

