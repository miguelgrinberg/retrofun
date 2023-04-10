import sqlalchemy as sa
from .models import Order, OrderItem, Customer, Product


def paginated_orders(start, length, sort, search):
    # base query to retrieve orders with their total amount
    total = sa.func.sum(OrderItem.quantity * OrderItem.unit_price).label(None)
    q = (
        sa.select(Order, total)
            .join(Order.customer)
            .join(Order.order_items)
            .join(OrderItem.product)
            .group_by(Order)
            .distinct()
    )

    # add search filters
    if search:
        q = q.where(
            sa.or_(
                Customer.name.ilike(f'%{search}%'),
                Product.name.ilike(f'%{search}%'),
            )
        )

    # add sorting
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]  # first character is either + or -
            name = s[1:]  # rest of the string is the column name
            if name == 'customer':
                column = Customer.name
            elif name == 'total':
                column = total
            else:
                column = getattr(Order, name)
            if direction == '-':
                column = column.desc()
            order.append(column)
        q = q.order_by(*order)

    # add pagination
    q = q.offset(start).limit(length)

    return q


def total_orders(search):
    if not search:
        return sa.select(sa.func.count(Order.id))

    return (
        sa.select(sa.func.count(sa.distinct(Order.id)))
            .join(Order.customer)
            .join(Order.order_items)
            .join(OrderItem.product)
            .where(
                sa.or_(
                    Customer.name.ilike(f'%{search}%'),
                    Product.name.ilike(f'%{search}%'),
                )
            )
    )
