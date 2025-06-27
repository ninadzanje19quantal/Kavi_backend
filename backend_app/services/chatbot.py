#libraries
from google import genai


#python scripts
from backend_app.constants import *



def chatbot_function(prompt: str, data: list | str = "") -> str:
    prompt = f"{prompt} {data}"

    client = genai.Client(api_key=gemini_api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text
