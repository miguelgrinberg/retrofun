from flask import Blueprint, render_template, request
from .models import db
from . import queries

bp = Blueprint('routes', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/api/orders')
def get_orders():
    start = request.args.get('start')
    length = request.args.get('length')
    sort = request.args.get('sort')
    search = request.args.get('search')

    data_query = queries.paginated_orders(start, length, sort, search)
    total_query = queries.total_orders(search)

    orders = db.session.execute(data_query)
    data = [{**o[0].to_dict(), 'total': o[1]} for o in orders]
    return {
        'data': data,
        'total': db.session.scalar(total_query),
    }
