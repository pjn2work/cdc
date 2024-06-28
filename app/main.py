from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from starlette.staticfiles import StaticFiles

from .db import init_db, get_db
from .web.index import router as web_index
from .api.dues_payments import router as dues_payments_router
from .api.members import router as members_router
from .api.member_due_payment import router as member_due_payment_router
from .web.members import router as web_members_router
from .web.member_due_payment import router as web_member_due_payment_router
from .web.dues_payments import router as web_dues_payments_router
from .dash_app.dash_app import app as dashboard1
from . import logit, logging

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logit("--- CdC Ready! ---", level=logging.WARNING)
    yield
    get_db().close()
    logit("--- CdC Closed! ---", level=logging.WARNING)


app = FastAPI(lifespan=lifespan, debug=False)

# APIs
app.include_router(members_router, prefix="/api/members", tags=["/api/members"])
app.include_router(dues_payments_router, prefix="/api/dues_payments", tags=["/api/dues_payments"])
app.include_router(member_due_payment_router, prefix="/api/member_due_payment", tags=["/api/member_due_payment"])

# Web pages
app.include_router(web_index, prefix="/web", tags=["/web"])
app.include_router(web_members_router, prefix="/web/members", tags=["/web/members"])
app.include_router(web_dues_payments_router, prefix="/web/dues_payments", tags=["/web/dues_payments"])
app.include_router(web_member_due_payment_router, prefix="/web/member_due_payment", tags=["/web/member_due_payment"])

# Web dashboards
#app.mount("/web/dashboard1", WSGIMiddleware(dashboard1.server))

# static files folder
app.mount("/", StaticFiles(directory="app/web/static"), name="static")

# uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
