from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app import logit, logging
from app.api.dues_payments import router as dues_payments_router
from app.api.items import router as items_router
from app.api.member_due_payment import router as member_due_payment_router
from app.api.members import router as members_router
from app.api.sellers import router as sellers_router
from app.db import init_db, get_db
from app.sec import router as sec_router
from app.web.dues_payments import router as web_dues_payments_router
from app.web.index import router as web_index
from app.web.login import router as login_router
from app.web.member_due_payment import router as web_member_due_payment_router
from app.web.members import router as web_members_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logit("--- CECC Ready! ---", level=logging.WARNING)
    yield
    get_db().close()
    logit("--- CECC Closed! ---", level=logging.WARNING)


app = FastAPI(lifespan=lifespan, debug=False)

@app.get(path="/health")
def health():
    return "I'm alive"

# Security
app.include_router(sec_router, prefix="/oauth", tags=["/oauth"])

# APIs
app.include_router(members_router, prefix="/api/members", tags=["/api/members"])
app.include_router(dues_payments_router, prefix="/api/dues_payments", tags=["/api/dues_payments"])
app.include_router(member_due_payment_router, prefix="/api/member_due_payment", tags=["/api/member_due_payment"])
app.include_router(sellers_router, prefix="/api/sellers", tags=["/api/sellers"])
app.include_router(items_router, prefix="/api/items", tags=["/api/items"])

# Web pages
app.include_router(web_index, prefix="/web", tags=["/web"])
app.include_router(login_router, prefix="/web/login", tags=["/web/login"])
app.include_router(web_members_router, prefix="/web/members", tags=["/web/members"])
app.include_router(web_dues_payments_router, prefix="/web/dues_payments", tags=["/web/dues_payments"])
app.include_router(web_member_due_payment_router, prefix="/web/member_due_payment", tags=["/web/member_due_payment"])

# Web dashboards
#app.mount("/web/dashboard1", WSGIMiddleware(dashboard1.server))

# static files folder
app.mount("/", StaticFiles(directory="app/web/static"), name="static")

# uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-config app/log.ini --reload
