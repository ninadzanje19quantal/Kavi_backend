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

current_work: str = "Using the following text as a context ask a question in one sentence" \
                    "Let’s start with your work — just so I get a sense of the world you operate in." \
                    "What’s your current role, and how long have you been doing it?" \
                    "If it’s easier, feel free to link your LinkedIn or drop a resume — totally up to you."

reason_for_interview: str = "Using the following text as a context ask a question in one sentence" \
                            "What’s got you preparing for interviews right now?" \
                            "You don’t need a perfect answer — just what’s true for you." \
                            "Some folks are job hunting after a layoff. Others are aiming for a big move — a promotion, a better offer, a dream company. " \
                            "And some just want to get better at telling their story. Which of those feels most like your situation?"

where_in_interview_process: str  ="Using the following text as a context ask a question in one sentence"\
                                  "Just so I know how fast to go — where are you in your interview process?"\
                                  "Still early? Already in the loop? Just sharpening up?"\
                                  "No pressure either way. This just helps me meet you where you are."

target_company: str = "Using the following text as a context ask a question in one sentence"\
                      "Any particular role or company you’ve got your eye on?"\
                      "You can type something like “PM at Google” or “Marketing lead at a Series A startup.”"\
                      "Or upload a job description if you’ve got one handy."\
                      "And if you're still figuring it out, that’s totally fine — we can start general and narrow in as you go."
