from fastapi import APIRouter

from app.api.v1.app.events import router as app_events_router
from app.api.v1.app.venues import router as app_venues_router
from app.api.v1.app.artworks import router as app_artworks_router
from app.api.v1.app.visits import router as app_visits_router
from app.api.v1.admin.auth import router as admin_auth_router
from app.api.v1.admin.events import router as admin_events_router
from app.api.v1.admin.venues import router as admin_venues_router
from app.api.v1.admin.artworks import router as admin_artworks_router
from app.api.v1.admin.upload import router as admin_upload_router
from app.api.v1.admin.stats import router as admin_stats_router

api_v1_router = APIRouter()

# Mobile app routes (public)
api_v1_router.include_router(app_events_router, prefix="/app")
api_v1_router.include_router(app_venues_router, prefix="/app")
api_v1_router.include_router(app_artworks_router, prefix="/app")
api_v1_router.include_router(app_visits_router, prefix="/app")

# Admin CMS routes (authenticated)
api_v1_router.include_router(admin_auth_router, prefix="/admin")
api_v1_router.include_router(admin_events_router, prefix="/admin")
api_v1_router.include_router(admin_venues_router, prefix="/admin")
api_v1_router.include_router(admin_artworks_router, prefix="/admin")
api_v1_router.include_router(admin_upload_router, prefix="/admin")
api_v1_router.include_router(admin_stats_router, prefix="/admin")
