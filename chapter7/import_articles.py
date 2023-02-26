import asyncio
import csv
from datetime import datetime
from sqlalchemy import select, delete
from db import Session
from models import BlogArticle, BlogAuthor, Product, BlogView, BlogSession, \
    BlogUser


async def main():
    async with Session() as session:
        async with session.begin():
            await session.execute(delete(BlogView))
            await session.execute(delete(BlogSession))
            await session.execute(delete(BlogUser))
            await session.execute(delete(BlogArticle))
            await session.execute(delete(BlogAuthor))

    async with Session() as session:
        async with session.begin():
            all_authors = {}
            all_products = {}

            with open('articles.csv') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    author = all_authors.get(row['author'])
                    if author is None:
                        author = BlogAuthor(name=row['author'])
                        all_authors[author.name] = author

                    product = None
                    if row['product']:
                        product = all_products.get(row['product'])
                        if product is None:
                            product = await session.scalar(
                                select(Product).where(
                                    Product.name == row['product']))
                            all_products[product.name] = product

                    article = BlogArticle(
                        title=row['title'],
                        author=author,
                        product=product,
                        timestamp=datetime.strptime(
                            row['timestamp'], '%Y-%m-%d %H:%M:%S'
                        ),
                    )
                    session.add(article)


if __name__ == '__main__':
    asyncio.run(main())
