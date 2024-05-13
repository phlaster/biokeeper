from fastapi.routing import APIRouter
from db_manager import DBM


router = APIRouter()

@router.get('/kits')
def get_kits():
    return DBM.kits.get_all()

@router.get('/kits/{kit_id}')
def get_kit(kit_id):
    return DBM.kits.get_info(kit_id)

@router.get('/kits/{kit_id}/status')
def get_kit_status(kit_id):
    return DBM.kits.status_of(kit_id)



@router.post('/kits')
def create_kit(n_qrs: int):
    return DBM.kits.new(n_qrs)