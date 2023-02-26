import asyncio
import csv
from datetime import datetime
from sqlalchemy import select, delete
from db import Session
from models import Product, Customer, Order, OrderItem


async def main():
    async with Session() as session:
        async with session.begin():
            await session.execute(delete(OrderItem))
            await session.execute(delete(Order))
            await session.execute(delete(Customer))

    async with Session() as session:
        async with session.begin():
            with open('orders.csv') as f:
                reader = csv.DictReader(f)
                all_customers = {}
                all_products = {}

                for row in reader:
                    if row['name'] not in all_customers:
                        c = Customer(name=row['name'], address=row['address'],
                                     phone=row['phone'])
                        all_customers[row['name']] = c
                    o = Order(
                        timestamp=datetime.strptime(row['timestamp'],
                                                    '%Y-%m-%d %H:%M:%S'),
                    )
                    all_customers[row['name']].orders.add(o)
                    session.add(o)

                    product = all_products.get(row['product1'])
                    if product is None:
                        product = await session.scalar(select(Product).where(
                            Product.name == row['product1']))
                        all_products[row['product1']] = product
                    o.order_items.append(OrderItem(
                        product=product,
                        unit_price=float(row['unit_price1']),
                        quantity=int(row['quantity1'])))

                    if row['product2']:
                        product = all_products.get(row['product2'])
                        if product is None:
                            product = await session.scalar(select(
                                Product).where(
                                    Product.name == row['product2']))
                            all_products[row['product2']] = product
                        o.order_items.append(OrderItem(
                            product=product,
                            unit_price=float(row['unit_price2']),
                            quantity=int(row['quantity2'])))

                    if row['product3']:
                        product = all_products.get(row['product3'])
                        if product is None:
                            product = await session.scalar(select(
                                Product).where(
                                    Product.name == row['product3']))
                            all_products[row['product3']] = product
                        o.order_items.append(OrderItem(
                            product=product,
                            unit_price=float(row['unit_price3']),
                            quantity=int(row['quantity3'])))


if __name__ == '__main__':
    asyncio.run(main())
