from fastapi import APIRouter
from app.schemas.user_schemas import AppInfoResponse

router = APIRouter(prefix="/api/v1/info", tags=["기타 정보"])

# 앱 정보 조회 
@router.get("/app", response_model=AppInfoResponse, summary="앱 버전 및 약관 정보")
async def get_app_info():
    return {
        "app_version": "1.0.0",
        "terms_url": "",
        "privacy_url": "" # 여따 우리 앱 정보 채우면 됨
    }