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
"""uvicorn backend_app.api.routes:kavi --reload --port 8000"""

user_chat_data = user_data()
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

#Scrape the LinkedIn data and summarize it
@kavi.post("/linkedin-scraper/")
async def linkedin_scraper_endpoint(request: LinkedInRequest):
    result = linkedin_scrapper(
        profile_url=request.profile_url
    )
    user_data.linkedin_data = result
    return {"linkedin_data": user_data.linkedin_data}



#################################################################################################
#                                      Chatbot Flow
#################################################################################################
@kavi.post("/chatbot/welcome")
async def chat_bot_welcome(final_prompt : chatbot_prompt_obj) -> str:
    final_prompt.prompt = welcome_prompt
    final_prompt.data = ""
    response = chatbot_function(final_prompt.prompt, final_prompt.data)
    return response

#Current Work
@kavi.post("/chatbot/current-work")
async def chat_bot_current_work(final_prompt : chatbot_prompt_obj) -> str:
    #What is your current work
    final_prompt.prompt = current_work
    response = chatbot_function(final_prompt.prompt, final_prompt.data)
    return response

@kavi.get("/chatbot/current-work")
async def user_current_work(current_work: str = Query(title="User Current Work",
                                                      description="User will enter his current work",
                                                      min_length=3)):
    user_data.current_work = current_work
    return {"current_work": user_data.current_work}


#Reason for interview
@kavi.post("/chatbot/reason-interview")
async def chat_bot_reason_interview(final_prompt : chatbot_prompt_obj) -> str:
    #What is the reason you are giving the interview
    final_prompt.prompt = reason_for_interview
    response = chatbot_function(final_prompt.prompt, final_prompt.data)
    return response

@kavi.get("/chatbot/reason-interview")
async def user_reason_interview(user_response: str = Query(title="User Current Work",
                                                      description="User will enter his current work",
                                                      min_length=3)):
    user_data.reason_for_interview = user_response
    return {"reason_for_interview": user_data.reason_for_interview}

#Where in Interview Process
@kavi.post("/chatbot/interview-process")
async def chat_bot_interview_process(final_prompt : chatbot_prompt_obj) -> str:
    #Where are you in the interview process
    final_prompt.prompt = where_in_interview_process
    response = chatbot_function(final_prompt.prompt, final_prompt.data)
    return response

@kavi.get("/chatbot/interview-process")
async def user_interview_process(user_response: str = Query(title="User Current Interview Process",
                                                            description="Where is the user currently in the interview process",
                                                            min_length=3)):
    user_data.current_interview_process = user_response
    return {"current_interview_process": user_data.current_interview_process}

#Target Company
@kavi.post("/chatbot/target-company")
async def chat_bot_target_company(final_prompt : chatbot_prompt_obj) -> str:
    #Any specific company you are targeting
    final_prompt.prompt = target_company
    response = chatbot_function(final_prompt.prompt, final_prompt.data)
    return response

@kavi.get("/chatbot/target-company")
async def user_target_company(user_response: str = Query(title="User Target Company",
                                                         description="What Company is the user targeting",
                                                         min_length=3)):
    user_data.target_company = user_response
    return {"target_comapny": user_data.target_company}


#Generate the onboarding summary
@kavi.get("/get-onboarding-summary")
async def get_onboarding_summary() -> str:
    data_used_for_summary = [user_chat_data.cv_data, user_chat_data.linkedin_data,
                             f"Current Work: {user_chat_data.current_work}",
                             f"Reason for giving the interview {user_chat_data.reason_for_interview}",
                             f"Current place in Interview process {user_chat_data.current_interview_process}",
                             f"Target Company: {user_chat_data.target_company}"]
    onboarding_summary = chatbot_function(onboarding_summary_prompt, data_used_for_summary)
    user_chat_data.user_summary = onboarding_summary
    return onboarding_summary

#Get user data (Testing purpose)
@kavi.get("/user_info")
async def get_user_info(user_data_obj) -> dict:
    user_data_dict: dict = user_data_obj
    return user_data_dict