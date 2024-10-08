from fastapi import APIRouter

from app.api.routes import items, login, users, utils, business, business_industry, employee, product_group, product, product_tag, lead, proposal

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(business_industry.router, prefix="/business_industry", tags=["business_industry"])
api_router.include_router(business.router, prefix="/business", tags=["business"])
api_router.include_router(employee.router, prefix="/employee", tags=["employee"])
api_router.include_router(product_group.router, prefix="/product_group", tags=["product_group"])
api_router.include_router(product.router, prefix="/product", tags=["product"])
api_router.include_router(product_tag.router, prefix="/product_tag", tags=["product_tag"])
api_router.include_router(lead.router, prefix="/lead", tags=["lead"])
api_router.include_router(proposal.router, prefix="/proposal", tags=["proposal"])
