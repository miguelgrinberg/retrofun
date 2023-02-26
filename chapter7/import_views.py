import asyncio
import csv
from datetime import datetime
from uuid import UUID
from sqlalchemy import select, delete
from db import Session
from models import BlogArticle, BlogUser, BlogView, BlogSession, Customer


async def main():
    async with Session() as session:
        async with session.begin():
            await session.execute(delete(BlogView))
            await session.execute(delete(BlogSession))
            await session.execute(delete(BlogUser))

    async with Session() as session:
        all_articles = {}
        all_customers = {}
        all_blog_users = {}
        all_blog_sessions = {}

        with open('views.csv') as f:
            reader = csv.DictReader(f)

            i = 0
            for row in reader:
                user = all_blog_users.get(row['user'])
                if user is None:
                    customer = None
                    if row['customer']:
                        customer = all_customers.get(row['customer'])
                        if customer is None:
                            customer = await session.scalar(
                                select(Customer).where(
                                    Customer.name == row['customer']))
                        all_customers[customer.name] = customer

                    user_id = UUID(row['user'])
                    user = BlogUser(id=user_id, customer=customer)
                    session.add(user)
                    all_blog_users[row['user']] = user

                blog_session = all_blog_sessions.get(row['session'])
                if blog_session is None:
                    session_id = UUID(row['session'])
                    blog_session = BlogSession(id=session_id, user=user)
                    session.add(blog_session)
                    all_blog_sessions[row['session']] = blog_session

                article = all_articles.get(row['title'])
                if article is None:
                    article = await session.scalar(select(BlogArticle).where(
                        BlogArticle.title == row['title']))
                all_articles[article.title] = article

                view = BlogView(
                    article=article,
                    session=blog_session,
                    timestamp=datetime.strptime(
                        row['timestamp'], '%Y-%m-%d %H:%M:%S'),
                )
                session.add(view)

                i += 1
                if i % 100 == 0:
                    print(i)
                    await session.commit()
            print(i)
            await session.commit()


if __name__ == '__main__':
    asyncio.run(main())
