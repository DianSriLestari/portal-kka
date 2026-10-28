from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.config import STATIC_DIR, UPLOADS_DIR
from app.database import init_tables
from app.routers import auth_router, guru_router, siswa_router, api_router

app = FastAPI(
    title="Portal Pembelajaran Koding & Kecerdasan Artifisial (KKA) Fase E",
    description="Web Portal Modul Ajar Interaktif berbasis Naskah Akademik Pembelajaran Mendalam (SMA Negeri 7 Pontianak)",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static and upload files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Include Routers
app.include_router(auth_router.router)
app.include_router(guru_router.router)
app.include_router(siswa_router.router)
app.include_router(api_router.router)

# Custom exception handler for 307 redirects raised by web dependencies
@app.exception_handler(307)
async def redirect_handler(request: Request, exc):
    return RedirectResponse(url=exc.headers.get("Location", "/login"))

@app.on_event("startup")
def on_startup():
    init_tables()
    print("[PORTAL] Aplikasi Portal Pembelajaran KKA siap digunakan!")
