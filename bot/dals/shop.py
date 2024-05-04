from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.cart import Cart, CartProduct
from models.category import Category, BaseCategory
from models.product import Product


class CategoryDAL:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_category(self, language: str, category_id: int) -> Category:
        stmt = select(Category).where(Category.master_id == category_id, Category.language_code == language)
        category = await self.session.execute(stmt)
        return category.scalars().first()

    async def get_categories(self, language: str):
        stmt_base = select(BaseCategory).where(BaseCategory.parent_id == None)
        base_categories = await self.session.execute(stmt_base)
        base_categories_ids = [base_category.id for base_category in base_categories.scalars().all()]
        stmt = select(Category).where(Category.language_code == language, Category.master_id.in_(base_categories_ids))
        categories = await self.session.execute(stmt)
        return categories.scalars().all()

    async def get_subcategories(self, language: str, category_id):
        stmt_base = select(BaseCategory).where(BaseCategory.parent_id == category_id)
        subcategories = await self.session.execute(stmt_base)
        if subcategories:
            subcategories_ids = [subcategory.id for subcategory in subcategories.scalars().all()]
            stmt = select(Category).where(Category.language_code == language, Category.master_id.in_(subcategories_ids))
            subcategories = await self.session.execute(stmt)
            return subcategories.scalars().all()
        return False

    async def get_category_by_title(self, title: str):
        stmt = select(Category).where(Category.title == title)
        category = await self.session.execute(stmt)
        return category.scalars().first()


class ProductDAL:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_product(self, language: str, product_id: int) -> Product:
        stmt = select(Product).where(Product.master_id == product_id, Product.language_code == language)
        product = await self.session.execute(stmt)
        return product.scalars().first()

    async def get_products(self, language: str, category_id: int):
        stmt = select(Product).where(Product.language_code == language, Product.category_id == category_id)
        products = await self.session.execute(stmt)
        return products.scalars().all()

    async def get_product_by_title(self, title: str):
        stmt = select(Product).where(Product.title == title)
        product = await self.session.execute(stmt)
        return product.scalars().first()

class CartDAL:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_cart(self, telegram_user_id: int):
        stmt = select(Cart).where(Cart.telegram_user_id == telegram_user_id)
        cart = await self.session.execute(stmt)
        return cart.scalars().first()

    async def create_cart(self, telegram_user_id: int):
        stmt = insert(Cart).values(telegram_user_id=telegram_user_id).returning(Cart.id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        await self.session.close()
        return result.fetchone()[0]

    async def get_product_from_cart(self, cart_id: int, product_id: int):
        stmt = select(CartProduct).where(CartProduct.cart_id == cart_id, CartProduct.product_id == product_id)
        product = await self.session.execute(stmt)
        return product.scalars().first()

    async def add_product_to_cart(self, cart_id: int, product_id: int, quantity: int):
        order_product = await self.get_product_from_cart(cart_id, product_id)
        if order_product:
            stmt = update(CartProduct).where(CartProduct.cart_id == cart_id,
                                             CartProduct.product_id == product_id).values(
                quantity=order_product.quantity + quantity)
            await self.session.execute(stmt)
            await self.session.commit()
            await self.session.close()
            return True
        stmt = insert(CartProduct).values(cart_id=cart_id, product_id=product_id, quantity=quantity)
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.close()
        return True

    async def remove_product_from_cart(self, cart_id: int, cart_product_id: int):
        stmt = delete(CartProduct).where(CartProduct.cart_id == cart_id, CartProduct.product_id==cart_product_id)
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.close()
        return True

    async def get_cart_products(self, cart_id: int):
        stmt = select(CartProduct).where(CartProduct.cart_id == cart_id)
        products = await self.session.execute(stmt)
        return products.scalars().all()

    async def get_total_price(self, cart_id):
        cart_products = await self.get_cart_products(cart_id)
        total_price = 0
        for cart_product in cart_products:
            product_dal = ProductDAL(self.session)
            product = await product_dal.get_product('ru', cart_product.product_id)
            total_price += product.price * cart_product.quantity
        return total_price

    async def clear_cart(self, cart_id: int):
        for cart_product in await self.get_cart_products(cart_id):
            await self.remove_product_from_cart(cart_id, cart_product.product_id)
        return True
