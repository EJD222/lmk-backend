import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.middleware.cors import add_cors
from app.middleware.rate_limit import limiter

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
from app.routers import sessions, participants, answers
from app.utils.http import HTTPStatusCode

app = FastAPI(title="lmk API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

add_cors(app)

app.include_router(sessions.router)
app.include_router(participants.router)
app.include_router(answers.router)


app.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent / "static", html=True), name="static")


@app.get("/", status_code=HTTPStatusCode.OK)
async def root():
    return {"status": "ok"}
