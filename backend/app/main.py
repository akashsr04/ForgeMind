import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import setup_logging, logger
from app.core.errors import (
    ForgeMindException,
    forgemind_exception_handler,
    generic_exception_handler,
)
from app.infrastructure.db.session import init_db
from app.api.routes import (
    health,
    overview,
    assets,
    incidents,
    investigations,
    simulations,
    recommendations,
    documents,
    model,
)

settings = get_settings()
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ForgeMind database and runtime services...")
    init_db()
    yield
    logger.info("ForgeMind application shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Agentic Industrial Intelligence & Digital Twin Operations Workbench. "
        "Provides asset graph topology, telemetry anomaly detection, LangGraph "
        "investigation workflow, Qdrant maintenance RAG, and discrete-event digital twin simulation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
origins = [
    settings.FRONTEND_ORIGIN,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID & Timing Middleware
@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    process_time = round((time.time() - start_time) * 1000.0, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = str(process_time)
    return response


# Register Exception Handlers
app.add_exception_handler(ForgeMindException, forgemind_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include Routers under API_V1_PREFIX
prefix = settings.API_V1_PREFIX
app.include_router(health.router, prefix=prefix)
app.include_router(health.router)  # also expose /health at root
app.include_router(overview.router, prefix=prefix)
app.include_router(assets.router, prefix=prefix)
app.include_router(incidents.router, prefix=prefix)
app.include_router(investigations.router, prefix=prefix)
app.include_router(simulations.router, prefix=prefix)
app.include_router(recommendations.router, prefix=prefix)
app.include_router(documents.router, prefix=prefix)
app.include_router(model.router, prefix=prefix)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "api_v1": settings.API_V1_PREFIX,
        "mode": "standalone_local_zero_paid_api",
    }
