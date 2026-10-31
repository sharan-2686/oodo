from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.customers import router as customers_router
from app.api.v1.endpoints.products import router as products_router
from app.api.v1.endpoints.plans import router as plans_router
from app.api.v1.endpoints.discounts import router as discounts_router
from app.api.v1.endpoints.taxes import router as taxes_router
from app.api.v1.endpoints.quotations import router as quotations_router
from app.api.v1.endpoints.subscriptions import router as subscriptions_router
from app.api.v1.endpoints.invoices import router as invoices_router
from app.api.v1.endpoints.payments import router as payments_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(customers_router)
api_router.include_router(products_router)
api_router.include_router(plans_router)
api_router.include_router(discounts_router)
api_router.include_router(taxes_router)
api_router.include_router(quotations_router)
api_router.include_router(subscriptions_router)
api_router.include_router(invoices_router)
api_router.include_router(payments_router)
api_router.include_router(dashboard_router)
