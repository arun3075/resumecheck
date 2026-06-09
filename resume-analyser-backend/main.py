from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyse

app = FastAPI(title="Resume Analyser API", version="1.0.0")

# Allow typical local development origins and any subdomain/domain for the deployed app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "https://localhost:5001",
        "http://localhost:5076",
        "https://localhost:5076",
        "http://localhost:5173",
        "http://localhost:5200",
        "http://localhost:5244",
        "https://your-app.azurestaticapps.net",
        "*"  # Allow all origins for seamless development/testing
    ],
    allow_credentials=False,  # Must be False if allow_origins includes "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyse.router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Resume Analyser API"}
