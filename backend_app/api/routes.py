#libraries
import io
from fastapi import FastAPI, Query, UploadFile, File, HTTPException
import uvicorn
from dotenv import load_dotenv
import os

from nipype.info import description
from pydantic import BaseModel
from pymupdf import pymupdf
from starlette.middleware.cors import CORSMiddleware
import json

#python scripts
from ..services import extract_text_from_cv
from ..services.linkedin_scrapepr import linkedin_scrapper
from ..services.chatbot import chatbot_function
from .schemas import *
from ..constants import *
from ..database.schema import *
#from backend_app.rag.vector_db import *
from backend_app.rag.querying import *
from backend_app.rag.response_generator import *

kavi = FastAPI()


kavi.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000", "https://your-production-frontend.com"],
    allow_origins=["*"], # Adjust this for production!

    allow_credentials=True, # Allow cookies to be included in requests
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], # Allow specific HTTP methods, "*" allows all
    allow_headers=[""], # Allow specific headers, "" allows all standard and non-standard headers
)
#For running the backend use
"""uvicorn backend_app.api.routes:kavi --reload --port 8000"""


#Default Home route
@kavi.get("/")
async def home():
    return {"Hello": "World"}

#Read the user CV
@kavi.post("/read-CV")
async def readCV(cv: UploadFile = File(...)):
    cv_data = extract_text_from_cv(cv)
    user_data["cv_data"] = cv_data
    return {"cv_data": user_data["cv_data"]}

#Scrape the LinkedIn data and summarize it
@kavi.post("/linkedin-scraper/")
async def linkedin_scraper_endpoint(request: LinkedInRequest):
    result = linkedin_scrapper(
        profile_url=request.profile_url
    )
    user_data["linkedin_data"] = chatbot_function(linkedin_prompt, result)
    return {"linkedin_data": user_data["linkedin_data"]}


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
    user_data["current_work"] = current_work
    return {"current_work": user_data["current_work"]}


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
    user_data["reason_for_interview"] = user_response
    return {"reason_for_interview": user_data["reason_for_interview"]}

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
    user_data["current_interview_process"] = user_response
    return {"current_interview_process": user_data["current_interview_process"]}

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
    user_data["target_company"] = user_response
    return {"target_comapny": user_data["target_company"]}



class CandidateProfileSchema(BaseModel):
    name: str
    location: str
    current_position: str
    current_company: str
    start_date: str
    company_size: str
    education: str
    skills: list[str]
    certifications: list[str]
    linkedin_url: str

class InterviewGoalsSchema(BaseModel):
    career_stage: str
    interview_reason: str
    interview_stage: str
    target_company: str
    search_scope: str

class OnboardingPayload(BaseModel):
    candidate_profile: CandidateProfileSchema
    interview_goals: InterviewGoalsSchema

#Generate the onboarding summary
@kavi.post("/onboarding/process")
def process_onboarding_data(payload: OnboardingPayload,
                            #authentication_id
                            ):
    data_as_dict = payload.model_dump()
    onboarding_summary = chatbot_function(onboarding_summary_prompt, data_as_dict)
    data_as_dict["onboarding_summary"] = onboarding_summary
    """add_user(
        auth_ID=authentication_id,
        name="",
        email="",
        linkedin_data="",
        linkedin_url="",
        cv_dta=""
    )"""
    return {"onboarding_summary": onboarding_summary}

class PlanPayload(BaseModel):
    default_query: str = interviewer_question_fetch_prompt
    user_summary: str
    number_of_result: int = 10

@kavi.post("/user-plan")
def user_plan(payload: PlanPayload):
    user_query = make_query(
               payload.default_query,
               payload.user_summary,
               payload.number_of_result)

    plan_questions = generate_response(query=user_query["query"],
                                       results=user_query["results"])
    return plan_questions


#Get user data (Testing purpose)
@kavi.get("/user_info")
async def get_user_info(user_data_obj) -> dict:
    user_data_dict: dict = user_data_obj
    return user_data_dict

#"Sanjeev Yadav, a Mumbai-based Information Technology engineering student, is a Software Developer at Quantal AI (11-50 employees) since March 2025.  He possesses skills in GitHub, Unit Testing, API Development, and Go, with certifications in Java, Python, SQL, and Web Development.  He is in the beginning stages of his career and exploring opportunities at Google, aiming for a broad search initially before refining his focus. His LinkedIn profile is available at [https://www.linkedin.com/in/sanjeev-yadav-7349861a3/](https://www.linkedin.com/in/sanjeev-yadav-7349861a3/).\n"
