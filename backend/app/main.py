from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.profiles import router as profiles_router
from app.api.interactions import router as interactions_router
from app.api.realtime import router as realtime_router
from app.core.config import settings

# Create upload directories
os.makedirs(os.path.join(settings.MEDIA_ROOT, "profile_pictures"), exist_ok=True)

app = FastAPI(
    title="Matcha API",
    description="API for Matcha dating app",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #TODO: Change this settings.BACKEND_CORS_ORIGINS from env file
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

""" @app.get("/")
async def root():
    return {"message": "Welcome to Matcha API"} """


app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(profiles_router, prefix=f"{settings.API_V1_STR}/profiles", tags=["Profiles"])
app.include_router(interactions_router, prefix=f"{settings.API_V1_STR}/interactions", tags=["Interactions"])
app.include_router(realtime_router, prefix=f"{settings.API_V1_STR}/realtime", tags=["Real-time"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)