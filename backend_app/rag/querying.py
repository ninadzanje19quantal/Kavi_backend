import chromadb
from backend_app.rag.vector_db import embedding_fn

from backend_app.constants import interviewer_question_fetch_prompt

def make_query(default_query_prompt: str, summary_prompt: str, number_of_results: int = 10,
               collection_name: str = "test_db_for_kavi")-> dict[str, list]:
    chroma_client = chromadb.PersistentClient(path="backend_app/rag/chroma")
    try:
        collection = chroma_client.get_collection(name=collection_name)
    except:
        return {"Error": ["Collection does not exist"]}
    query = default_query_prompt + summary_prompt
    query_embeddings = embedding_fn([query])

    results = collection.query(
        query_embeddings=query_embeddings,
        n_results=number_of_results,
    )["documents"]

    return {"query": query, "results": results[0]}

query_and_results = make_query(interviewer_question_fetch_prompt,
            "Ninad Zanje, Artificial Intelligence Engineer at Quantal, India.\n\n**About:** Ninad focuses on Generative AI and Agentic AI initiatives, handling roadmap design, backend development, and client engagement, especially in text-to-text, speech-to-text, and text-to-image applications.\n\n**Skills:** Automation, Generative AI, Python, Computer Science.\n\n**Certifications:** Python Bootcamp (Udemy), Introduction to Julia (Julia Computing), Introduction to Quantum Computing (Qubit by Qubit).\n\n**Latest Job:** Artificial Intelligence Engineer at Quantal (since March 2025), driving generative AI initiatives and managing client communication."
               )
print(query_and_results)


"""
{    
  "candidate_profile": {
    "name": "Sanjeev Yadav",
    "location": "Mumbai, Maharashtra, India",
    "current_position": "Software Developer",
    "current_company": "Quantal AI",
    "start_date": "March 2025",
    "company_size": "11-50",
    "education": "Information Technology engineering student",
    "skills": [
      "GitHub",
      "Unit Testing",
      "API Development",
      "Go (Programming Language)"
    ],
    "certifications": [
      "Java (Basic)",
      "Google Digital Garage Certification",
      "Python (Basic)",
      "Web Development Internship",
      "SQL (Basic)"
    ],
    "linkedin_url": "https://www.linkedin.com/in/sanjeev-yadav-7349861a3/"
  },
  "interview_goals": {
    "career_stage": "Beginning",
    "interview_reason": "Career Start / Exploration",
    "interview_stage": "Initial",
    "target_company": "Google",
    "search_scope": "Broad with future refinement"
  }
}
"""