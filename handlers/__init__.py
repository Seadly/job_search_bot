from aiogram import Dispatcher
from .start import router as start_router
from .keywords import router as keywords_router
from .channels import router as channels_router
from .search import router as search_router
from .alerts import router as alerts_router


def setup_routers(dp: Dispatcher):
    from database import init_db
    init_db()

    dp.include_router(start_router)
    dp.include_router(keywords_router)
    dp.include_router(channels_router)
    dp.include_router(search_router)
    dp.include_router(alerts_router)
