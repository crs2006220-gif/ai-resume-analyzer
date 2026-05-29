from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import config

app = FastAPI(
    title="AI Resume Analysis System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from app.routers import matching, resume
    app.include_router(resume.router)
    app.include_router(matching.router)
except Exception:
    pass

try:
    import os
    if os.path.isdir("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    pass


@app.get("/")
async def root():
    from fastapi.responses import HTMLResponse
    import os
    html_path = os.path.join("static", "index.html")
    if os.path.isfile(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>AI Resume Analysis System</h1>")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get(f"{config.API_PREFIX}/health")
async def health_check_v1():
    return {"status": "ok"}
