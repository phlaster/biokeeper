from fastapi.routing import APIRouter
from db_manager import DBM
from datetime import datetime


router = APIRouter()


@router.get('/samples')
def get_samples():
    return DBM.samples.get_all()

@router.get('/samples/{sample_id}')
def get_sample(sample_id):
    return DBM.samples.get_info(sample_id)

@router.get('/samples/{sample_id}/status')
def get_sample_status(sample_id):
    return DBM.samples.status_of(sample_id)

@router.get('/samples/{sample_id}/gps')
def get_sample_gps(sample_id):
    return DBM.samples.get_info(sample_id)['gps']

@router.post('/samples')
def create_sample(
    qr_hex: str,
    research_name: str,
    collected_at: datetime,
    gps: str,#tuple[float, float],
    weather: str = None,
    user_comment: str = None,
    photo_hex: str = None
):
    return DBM.samples.new(bytes.fromhex(qr_hex), research_name, collected_at, gps, weather, user_comment, bytes.fromhex(photo_hex))