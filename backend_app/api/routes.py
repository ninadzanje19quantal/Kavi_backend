#libraries
import io
from fastapi import FastAPI, Query, UploadFile, File, HTTPException
import uvicorn
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from pymupdf import pymupdf


#python scripts
from ..services import extract_text_from_cv
from ..services.linkedin_scrapepr import linkedin_scrapper
from ..services.chatbot import chatbot_function
from .schemas import *
from ..constants import *

kavi = FastAPI()

#For running the backend use
#uvicorn routes:kavi --reload --port 8000


@kavi.get("/")
async def home():
    return {"Hello": "World"}

@kavi.post("/read-CV")
async def readCV(cv: UploadFile = File(...)):
    cv_data = extract_text_from_cv(cv)
    user_data.cv_data = cv_data
    return {"cv_data": user_data.cv_data}

@kavi.post("/linkedin-scraper/")
async def linkedin_scraper_endpoint(request: LinkedInRequest):
    result = linkedin_scrapper(
        profile_url=request.profile_url
    )
    user_data.linkedin_data = result
    return {"linkedin_data": user_data.linkedin_data}

@kavi.post("/chatbot/welcome")
async def chat_bot_welcome(final_prompt : chatbot_prompt) -> str:
    final_prompt.prompt = welcome_prompt
    final_prompt.data = ""
    response = chatbot_function(final_prompt.prompt, final_prompt.data)
    return response