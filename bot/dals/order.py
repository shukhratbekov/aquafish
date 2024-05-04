from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.order import Order, OrderProduct, OrderShipping


class OrderDAL:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create_order(
            self,
            telegram_user_id,
            payment,
            phone_number,
            status,
            final_price,
            shipping= False
    ):
        stmt = insert(Order).values(
            telegram_user_id=telegram_user_id,
            payment=payment,
            phone_number=phone_number,
            status=status,
            shipping=shipping,
            final_price=final_price,
        ).returning(Order.id)
        order_id = await self.session.execute(stmt)
        await self.session.commit()
        await self.session.close()
        return order_id.fetchone()[0]

    async def get_order(self, order_id):
        stmt = select(Order).where(Order.id == order_id)
        order = await self.session.execute(stmt)
        return order.scalars().first()

    async def get_orders(self, user_id):
        stmt = select(Order).where(Order.telegram_user_id == user_id)
        orders = await self.session.execute(stmt)
        return orders.scalars().all()

    async def create_order_product(self, order_id, product_id, quantity, price):
        stmt = insert(OrderProduct).values(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=price,
        )
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.close()
        return True

    async def create_order_shipping(self, order_id, address, longitude, latitude):
        stmt = insert(OrderShipping).values(
            order_id=order_id,
            address=address,
            longitude=longitude,
            latitude=latitude,
        )
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.close()
        return True

    async def get_customer_orders(self, telegram_user_id):
        stmt = select(Order).where(Order.telegram_user_id == telegram_user_id)
        orders = await self.session.execute(stmt)
        return orders.scalars().all()

    async def get_order_products(self, order_id):
        stmt = select(OrderProduct).where(OrderProduct.order_id == order_id)
        products = await self.session.execute(stmt)
        return products.scalars().all()

    async def get_order_shipping(self, order_id):
        stmt = select(OrderShipping).where(OrderShipping.order_id == order_id)
        shipping = await self.session.execute(stmt)
        return shipping.scalars().first()
