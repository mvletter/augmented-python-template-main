from fastapi import APIRouter

from service.adapters.http.endpoints import router


main_router = APIRouter()

main_router.include_router(router)
