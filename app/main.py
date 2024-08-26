from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from starlette.staticfiles import StaticFiles

from app import logit, logging, log_traffic
from app.api import error_json
from app.api.dues_payments import router as dues_payments_router
from app.api.items import router as items_router
from app.api.member_due_payment import router as member_due_payment_router
from app.api.members import router as members_router
from app.api.sellers import router as sellers_router
from app.api.tests import router as tests_router
from app.db import init_db, get_db
from app.sec import router as sec_router
from app.web import error_page
from app.web.admin import router as admin_router
from app.web.categories import router as web_items_categories_router
from app.web.dues_payments import router as web_dues_payments_router
from app.web.expense_accounts import router as web_sellers_ea_router
from app.web.index import router as web_index
from app.web.items import router as web_items_router
from app.web.login import router as login_router
from app.web.member_due_payment import router as web_member_due_payment_router
from app.web.members import router as web_members_router
from app.web.members_items import router as web_members_items_router
from app.web.sellers import router as web_sellers_router
from app.web.sellers_items import router as web_sellers_items_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logit("--- CECC Ready! ---", level=logging.WARNING)
    yield
    get_db().close()
    logit("--- CECC Closed! ---", level=logging.WARNING)


app = FastAPI(lifespan=lifespan, debug=False)
VERSION = "v0.11"


@app.middleware("https")
async def main_log_traffic(request: Request, call_next):
    kwargs = {
        "start_time": datetime.now(),
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host
    }
    try:
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        log_traffic(status_code=response.status_code, **kwargs)
    except Exception:
        log_traffic(status_code=501, **kwargs)
        raise

    return response


@app.get(path="/health")
def health():
    return f"I'm alive, running {VERSION}"


@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    if request.url.path.startswith("/web/"):
        return error_page(request, exc)
    return error_json(exc)


# Security
app.include_router(sec_router, prefix="/oauth", tags=["/oauth"])

# APIs
app.include_router(members_router, prefix="/api/members", tags=["/api/members"])
app.include_router(dues_payments_router, prefix="/api/dues_payments", tags=["/api/dues_payments"])
app.include_router(member_due_payment_router, prefix="/api/member_due_payment", tags=["/api/member_due_payment"])
app.include_router(sellers_router, prefix="/api/sellers", tags=["/api/sellers"])
app.include_router(items_router, prefix="/api/items", tags=["/api/items"])
app.include_router(tests_router, prefix="/api/tests", tags=["/api/tests"])

# Web pages
app.include_router(web_index, prefix="/web", tags=["/web"])
app.include_router(login_router, prefix="/web/login", tags=["/web/login"])
app.include_router(admin_router, prefix="/web/admin", tags=["/web/admin"])
app.include_router(web_members_router, prefix="/web/members", tags=["/web/members"])
app.include_router(web_dues_payments_router, prefix="/web/dues_payments", tags=["/web/dues_payments"])
app.include_router(web_member_due_payment_router, prefix="/web/member_due_payment", tags=["/web/member_due_payment"])
app.include_router(web_items_router, prefix="/web/items", tags=["/web/items"])
app.include_router(web_items_categories_router, prefix="/web/categories", tags=["/web/categories"])
app.include_router(web_sellers_router, prefix="/web/sellers", tags=["/web/sellers"])
app.include_router(web_sellers_ea_router, prefix="/web/expense-accounts", tags=["/web/expense-accounts"])
app.include_router(web_sellers_items_router, prefix="/web/sellers-items", tags=["/web/sellers-items"])
app.include_router(web_members_items_router, prefix="/web/members-items", tags=["/web/members-items"])

# Web dashboards
#app.mount("/web/dashboard1", WSGIMiddleware(dashboard1.server))

# static files folder
app.mount("/", StaticFiles(directory="app/web/static"), name="static")

# uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-config app/log.ini --reload
