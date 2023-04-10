from fastapi import APIRouter
from fastapi.responses import FileResponse
from .models import db
from . import queries

router = APIRouter()


@router.get('/')
async def index():
    return FileResponse('retrofun/html/index.html')


@router.get('/api/orders')
async def get_orders(start: int, length: int, sort: str = '',
                     search: str = ''):
    data_query = queries.paginated_orders(start, length, sort, search)
    total_query = queries.total_orders(search)

    async with db.Session() as session:
        orders = await session.stream(data_query)
        data = [{**o[0].to_dict(), 'total': o[1]} async for o in orders]
        return {
            'data': data,
            'total': await session.scalar(total_query),
        }
