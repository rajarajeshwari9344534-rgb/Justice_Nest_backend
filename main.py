from fastapi import FastAPI
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

from fastapi.middleware.cors import CORSMiddleware
from db.session import engine, Base

from routers.lawyer_route import lawyerrouter
from routers.complaint_route import complaint_router
from routers.userrouter import user_router
from routers.admin_route import admin_router
from routers.message_route import message_router

# Import models 
from models.user import User
from models.lawyers import Lawyers
from models.complaint import Complaints
from models.message import Messages
 
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# INCLUDE EACH ROUTER ONLY ONCE
app.include_router(lawyerrouter)
app.include_router(user_router)
app.include_router(complaint_router)
app.include_router(admin_router)
app.include_router(message_router)
 