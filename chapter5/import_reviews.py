import csv
from datetime import datetime
from sqlalchemy import select, delete
from db import Session
from models import Product, Customer, ProductReview


def main():
    with Session() as session:
        with session.begin():
            session.execute(delete(ProductReview))

    with Session() as session:
        with session.begin():
            with open('reviews.csv') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    c = session.scalar(select(Customer).where(
                        Customer.name == row['customer']))
                    p = session.scalar(select(Product).where(
                        Product.name == row['product']))
                    r = ProductReview(
                        customer=c,
                        product=p,
                        timestamp=datetime.strptime(row['timestamp'],
                                                    '%Y-%m-%d %H:%M:%S'),
                        rating=int(row['rating']),
                        comment=row['comment'] or None)
                    session.add(r)


if __name__ == '__main__':
    main()
