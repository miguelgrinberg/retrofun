import os
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import sqlalchemy as sa
import sqlalchemy.orm as so
from alchemical.aio import Alchemical

db = Alchemical(os.environ['DATABASE_URL'])

ProductCountry = sa.Table(
    'products_countries',
    db.Model.metadata,
    sa.Column('product_id', sa.ForeignKey('products.id'), primary_key=True,
              nullable=False),
    sa.Column('country_id', sa.ForeignKey('countries.id'), primary_key=True,
              nullable=False),
)


class Product(db.Model):
    __tablename__ = 'products'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    manufacturer_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('manufacturers.id'), index=True)
    year: so.Mapped[int] = so.mapped_column(index=True)
    cpu: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32))

    manufacturer: so.Mapped['Manufacturer'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='products')
    countries: so.Mapped[list['Country']] = so.relationship(
        lazy='selectin', secondary=ProductCountry, back_populates='products')
    order_items: so.WriteOnlyMapped['OrderItem'] = so.relationship(
        back_populates='product')
    reviews: so.WriteOnlyMapped['ProductReview'] = so.relationship(
        back_populates='product')
    blog_articles: so.WriteOnlyMapped['BlogArticle'] = so.relationship(
        back_populates='product')

    def __repr__(self):
        return f'Product({self.id}, "{self.name}")'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'manufacturer': self.manufacturer.to_dict(),
            'year': self.year,
            'cpu': self.cpu,
            'countries': [country.to_dict() for country in self.countries],
        }


class Manufacturer(db.Model):
    __tablename__ = 'manufacturers'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)

    products: so.Mapped[list['Product']] = so.relationship(
        lazy='selectin', cascade='all, delete-orphan',
        back_populates='manufacturer')

    def __repr__(self):
        return f'Manufacturer({self.id}, "{self.name}")'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Country(db.Model):
    __tablename__ = 'countries'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(32), index=True, unique=True)

    products: so.Mapped[list['Product']] = so.relationship(
        lazy='selectin', secondary=ProductCountry,
        back_populates='countries')

    def __repr__(self):
        return f'Country({self.id}, "{self.name}")'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Order(db.Model):
    __tablename__ = 'orders'

    id: so.Mapped[UUID] = so.mapped_column(default=uuid4, primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        default=datetime.utcnow, index=True)
    customer_id: so.Mapped[UUID] = so.mapped_column(
        sa.ForeignKey('customers.id'), index=True)

    customer: so.Mapped['Customer'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='orders')
    order_items: so.Mapped[list['OrderItem']] = so.relationship(
        lazy='selectin', back_populates='order')

    def __repr__(self):
        return f'Order({self.id.hex})'

    def to_dict(self):
        return {
            'id': self.id.hex,
            'timestamp': self.timestamp.isoformat(),
            'customer': self.customer.to_dict(),
            'order_items': [item.to_dict() for item in self.order_items],
        }


class Customer(db.Model):
    __tablename__ = 'customers'

    id: so.Mapped[UUID] = so.mapped_column(default=uuid4, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    phone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32))

    orders: so.WriteOnlyMapped['Order'] = so.relationship(
        back_populates='customer')
    product_reviews: so.WriteOnlyMapped['ProductReview'] = so.relationship(
        back_populates='customer')
    blog_users: so.WriteOnlyMapped['BlogUser'] = so.relationship(
        back_populates='customer')

    def __repr__(self):
        return f'Customer({self.id.hex}, "{self.name}")'

    def to_dict(self):
        return {
            'id': self.id.hex,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
        }


class OrderItem(db.Model):
    __tablename__ = 'orders_items'

    product_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('products.id'), primary_key=True)
    order_id: so.Mapped[UUID] = so.mapped_column(
        sa.ForeignKey('orders.id'), primary_key=True)
    unit_price: so.Mapped[float]
    quantity: so.Mapped[int]

    product: so.Mapped['Product'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='order_items')
    order: so.Mapped['Order'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='order_items')

    def to_dict(self):
        return {
            'product': self.product.to_dict(),
            'quantity': self.quantity,
            'unit_price': self.unit_price,
        }


class ProductReview(db.Model):
    __tablename__ = 'product_reviews'

    product_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('products.id'), primary_key=True)
    customer_id: so.Mapped[UUID] = so.mapped_column(
        sa.ForeignKey('customers.id'), primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        default=datetime.utcnow, index=True)
    rating: so.Mapped[int]
    comment: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)

    product: so.Mapped['Product'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='reviews')
    customer: so.Mapped['Customer'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='product_reviews')


class BlogArticle(db.Model):
    __tablename__ = 'blog_articles'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    author_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('blog_authors.id'), index=True)
    product_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey('products.id'), index=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        default=datetime.utcnow, index=True)
    language_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey('languages.id'), index=True)
    translation_of_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey('blog_articles.id'), index=True)

    author: so.Mapped['BlogAuthor'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='articles')
    product: so.Mapped[Optional['Product']] = so.relationship(
        lazy='joined', back_populates='blog_articles')
    views: so.WriteOnlyMapped['BlogView'] = so.relationship(
        back_populates='article')
    language: so.Mapped[Optional['Language']] = so.relationship(
        lazy='joined', back_populates='blog_articles')
    translation_of: so.Mapped[Optional['BlogArticle']] = so.relationship(
        lazy='joined', remote_side=id, back_populates='translations')
    translations: so.Mapped[list['BlogArticle']] = so.relationship(
        lazy='selectin', back_populates='translation_of')

    def __repr__(self):
        return f'BlogArticle({self.id}, "{self.title}")'


class BlogAuthor(db.Model):
    __tablename__ = 'blog_authors'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)

    articles: so.WriteOnlyMapped['BlogArticle'] = so.relationship(
        back_populates='author')

    def __repr__(self):
        return f'BlogAuthor({self.id}, "{self.name}")'


class BlogUser(db.Model):
    __tablename__ = 'blog_users'

    id: so.Mapped[UUID] = so.mapped_column(default=uuid4, primary_key=True)
    customer_id: so.Mapped[Optional[UUID]] = so.mapped_column(
        sa.ForeignKey('customers.id'), index=True)

    customer: so.Mapped[Optional['Customer']] = so.relationship(
        lazy='joined', back_populates='blog_users')
    sessions: so.WriteOnlyMapped['BlogSession'] = so.relationship(
        back_populates='user')

    def __repr__(self):
        return f'BlogUser({self.id.hex})'


class BlogSession(db.Model):
    __tablename__ = 'blog_sessions'

    id: so.Mapped[UUID] = so.mapped_column(default=uuid4, primary_key=True)
    user_id: so.Mapped[UUID] = so.mapped_column(
        sa.ForeignKey('blog_users.id'), index=True)

    user: so.Mapped['BlogUser'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='sessions')
    views: so.WriteOnlyMapped['BlogView'] = so.relationship(
        back_populates='session')

    def __repr__(self):
        return f'BlogSession({self.id.hex})'


class BlogView(db.Model):
    __tablename__ = 'blog_views'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    article_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('blog_articles.id'))
    session_id: so.Mapped[UUID] = so.mapped_column(
        sa.ForeignKey('blog_sessions.id'))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        default=datetime.utcnow, index=True)

    article: so.Mapped['BlogArticle'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='views')
    session: so.Mapped['BlogSession'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='views')


class Language(db.Model):
    __tablename__ = 'languages'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.String(32), index=True, unique=True)

    blog_articles: so.WriteOnlyMapped['BlogArticle'] = so.relationship(
        back_populates='language')

    def __repr__(self):
        return f'Language({self.id}, "{self.name}")'
