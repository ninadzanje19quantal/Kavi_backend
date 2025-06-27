from  dotenv import load_dotenv
import os

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
email = os.getenv("LINKEDIN_EMAIL")
password = os.getenv("LINKEDIN_PASSWORD")

cv_prompt: str = "Summarize the following information."

linkedin_prompt: str = ("Summarize the following information with particular focus on the "
                        "headline, about, skills, certifications, recommendations, activity and "
                        "details of their latest job. If a particular data field does not exist "
                        "then just ignore it.")

welcome_prompt: str = "Welcome the user in 2 sentences on our platform"
