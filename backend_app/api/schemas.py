#libraries
import os
from dotenv import load_dotenv
from pydantic import BaseModel


class LinkedInRequest(BaseModel):
    user_email: str = os.getenv("LINKEDIN_EMAIL")
    user_password: str = os.getenv("LINKEDIN_PASSWORD")
    profile_url: str

class chatbot_prompt(BaseModel):
    prompt: str
    data: str | tuple | list

class user_data(BaseModel):
    user_name: str = ""
    password: str= ""
    email: str= ""
    linkedin_data: str | list | None = None
    cv_data: str | None = None
    current_work: str= ""
    reason_for_interview: str= ""
    current_interview_process: str= ""
    target_company: str= ""
    user_summary: str= ""