from google import genai
from dotenv import load_dotenv
import os



load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def generate_response(query: str, results):
    # Build the context block from your retrieved Chroma documents
    context = "\n".join(results["documents"][0])  # Assuming you've already run collection.query()

    prompt = f""""You are an expert interview coach creating a personalized interview preparation plan for a candidate.\n\n"
        f"Candidate profile:\n{query}\n\n"
        "Below is a list of 10 relevant interview questions retrieved from a curated database. "
        "You must only work with these exact questions. Do NOT generate new questions.\n\n"
        f"{results}\n\n"
        "Your task:\n"
        "Select the most appropriate questions from the above list (only if suitable), and organize them into the following categories:\n"
        "1. Recruiter Screening Questions\n"
        "2. Hiring Manager Questions\n"
        "3. Onsite Interview Questions\n"
        "4. Final Round Interview Questions\n\n"
        "For each category, list up to 5 questions with a one-line coaching tip on how the candidate should approach it. "
        "If you cannot find good matches for a category, just leave it empty.\n\n"
        "Do not create new questions or hallucinate content.\n"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    ).text

    return response
