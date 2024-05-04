import uvicorn
from aiogram.types import Update

from fastapi import FastAPI, Request

from bot import bot, dp
from configs import WEBHOOK_URI, TOKEN

from middlewares import AuthMiddleware

from routers.start import router as start_router
from routers.shop import router as shop_router
from routers.settings import router as settings_router
from routers.order import router as order_router
from routers.view import router as view_router

app = FastAPI()


async def set_webhook():
    await bot.set_webhook(WEBHOOK_URI)


async def include_routers():
    dp.update.outer_middleware(AuthMiddleware())
    dp.include_routers(start_router)
    dp.include_routers(shop_router)
    dp.include_routers(settings_router)
    dp.include_routers(order_router)
    dp.include_routers(view_router)


async def on_startup():
    await set_webhook()
    await include_routers()


@app.on_event("startup")
async def startup():
    await on_startup()


@app.on_event("shutdown")
async def shutdown():
    await bot.delete_webhook()


@app.post(f'/bot/{TOKEN}')
async def create_item(request: Request):
    update = Update(**await request.json())
    await dp.feed_webhook_update(bot, update)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001)
