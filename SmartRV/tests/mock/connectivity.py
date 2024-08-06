from fastapi import APIRouter


router = APIRouter(
    prefix='/connectivity',
    tags=['CONNECTIVITY', ]
)

router.config = {}


@router.put('/login')
async def put_login():
    pass


@router.get('/gps')
async def get_gps():
    pass
