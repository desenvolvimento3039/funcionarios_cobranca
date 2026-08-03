import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import cobranca

from contextlib import asynccontextmanager
from app.tasks.scheduler import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()

app = FastAPI(
    title="Sicoob | Gestão de Funcionários de Cobrança",
    description="API de Gestão de Funcionários de Cobrança - Sincronização com bases LeCom e SicoobSMO",
    version="2.0.0",
    lifespan=lifespan
)

# Middleware para permitir exibição em iframe no Hub (IP 195) e outras origens
@app.middleware("http")
async def allow_iframe_middleware(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "frame-ancestors 'self' http://10.52.255.195 http://10.52.255.194 http://10.52.255.195:5862"
    if "X-Frame-Options" in response.headers:
        del response.headers["X-Frame-Options"]
    if "x-frame-options" in response.headers:
        del response.headers["x-frame-options"]
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:5500",
        "http://127.0.0.1",
        "http://10.52.255.195",
        "http://10.52.255.194",
        "http://10.52.255.195:5862"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cobranca.router)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"status": "running", "info": "Frontend não encontrado."}
