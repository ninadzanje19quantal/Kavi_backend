#libraries
from linkedin_api.linkedin import Linkedin

#files
from .chatbot import *
from backend_app.constants import linkedin_prompt

def convert_linkedin_url_to_id(url: str) -> str:
    if url.split("/")[-1] == "":
        linkedin_id = url.split("/")[-2]
    else:
        linkedin_id = url.split("/")[-1]
    return  linkedin_id


def linkedin_scrapper(profile_url: str) -> list | str:
    try:
        api = Linkedin(username=email, password=password)
    except:
        return "Incorrect Credentials"


    user_profile = convert_linkedin_url_to_id(profile_url)
    user_profile = user_profile.split(r"/")[-1]
    profile_data = api.get_profile(user_profile)
    profile_data = list(profile_data.items())

    if len(profile_data) == 0:
        return "Profile does not exist"

    profile_data = chatbot_function(linkedin_prompt, profile_data)

    return profile_data

#print(linkedin_scrapper("ninad-zanje"))
