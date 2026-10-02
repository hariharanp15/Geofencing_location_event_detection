from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from .routes import audit, devices, events, geofences, locations

app = FastAPI(title="Geofencing API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(geofences.router, prefix="/api")
app.include_router(devices.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(audit.router, prefix="/api")


@app.exception_handler(OperationalError)
async def database_unavailable(_: Request, __: OperationalError) -> JSONResponse:
    """Keep missing credentials and unavailable MySQL instances from surfacing as a 500."""
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database unavailable. Set DATABASE_URL in backend/.env with valid MySQL credentials, then run Alembic migrations.",
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}
