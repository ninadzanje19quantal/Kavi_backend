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
"""uvicorn routes:kavi --reload --port 8000"""

#Default Home route
@kavi.get("/")
async def home():
    return {"Hello": "World"}

#Read the user CV
@kavi.post("/read-CV")
async def readCV(cv: UploadFile = File(...)):
    cv_data = extract_text_from_cv(cv)
    user_data.cv_data = cv_data
    return {"cv_data": user_data.cv_data}

#Scrape the Linkedin data and summarize it
@kavi.post("/linkedin-scraper/")
async def linkedin_scraper_endpoint(request: LinkedInRequest):
    result = linkedin_scrapper(
        profile_url=request.profile_url
    )
    user_data.linkedin_data = result
    return {"linkedin_data": user_data.linkedin_data}

@kavi.post("/chatbot/welcome")
async def chat_bot_welcome(final_prompt : chatbot_prompt_obj) -> str:
    final_prompt.prompt = welcome_prompt
    final_prompt.data = ""
    response = chatbot_function(final_prompt.prompt, final_prompt.data)
    return response

@kavi.post("/chatbot/current-work")
async def chat_bot_current_work(final_prompt : chatbot_prompt_obj) -> str:
    #What is your current work
    final_prompt.prompt = current_work
    response = chatbot_function(final_prompt.prompt, final_prompt.data)
    return response

@kavi.post("/chatbot/reason-interview")
async def chat_bot_current_work(final_prompt : chatbot_prompt_obj) -> str:
    #What is the reason you are giving the interview
    final_prompt.prompt = reason_for_interview
    response = chatbot_function(final_prompt.prompt, final_prompt.data)
    return response

@kavi.post("/chatbot/interview-process")
async def chat_bot_current_work(final_prompt : chatbot_prompt_obj) -> str:
    #Where are you in the interview process
    final_prompt.prompt = where_in_interview_process
    response = chatbot_function(final_prompt.prompt, final_prompt.data)
    return response

@kavi.post("/chatbot/target-company")
async def chat_bot_current_work(final_prompt : chatbot_prompt_obj) -> str:
    #Any specific company you are targeting
    final_prompt.prompt = target_company
    response = chatbot_function(final_prompt.prompt, final_prompt.data)
    return response

@kavi.get("/get-onboarding-summary")
def get_onboarding_summary(user_data_obj) -> dict:
    user_data_dict: dict = user_data_obj
    return user_data_dict