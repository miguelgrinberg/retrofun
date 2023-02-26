import asyncio
import csv
from sqlalchemy import delete
from db import Session
from models import Product, Manufacturer, Country, ProductCountry


async def main():
    async with Session() as session:
        async with session.begin():
            await session.execute(delete(ProductCountry))
            await session.execute(delete(Product))
            await session.execute(delete(Manufacturer))
            await session.execute(delete(Country))

    async with Session() as session:
        async with session.begin():
            with open('products.csv') as f:
                reader = csv.DictReader(f)
                all_manufacturers = {}
                all_countries = {}

                for row in reader:
                    row['year'] = int(row['year'])

                    manufacturer = row.pop('manufacturer')
                    countries = row.pop('country').split('/')
                    p = Product(**row)

                    if manufacturer not in all_manufacturers:
                        m = Manufacturer(name=manufacturer)
                        session.add(m)
                        all_manufacturers[manufacturer] = m
                    all_manufacturers[manufacturer].products.append(p)

                    for country in countries:
                        if country not in all_countries:
                            c = Country(name=country)
                            session.add(c)
                            all_countries[country] = c
                        all_countries[country].products.append(p)


if __name__ == '__main__':
    asyncio.run(main())
