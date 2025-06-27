
import streamlit as st
import google.generativeai as genai
from linkedin_api import Linkedin  # For Linkedin Scraper
import pymupdf  # For PDF parsing (fitz)
import re  # For cleaning up LinkedIn profile ID


# --- LinkedIn Scraper Function (modified slightly for clarity) ---
def convert_linkedin_url_to_id(profile_url: str) -> str:
    """
    Extracts the public profile ID from a LinkedIn URL.
    Handles common URL formats like:
    - https://www.linkedin.com/in/username/
    - https://www.linkedin.com/in/username
    - www.linkedin.com/in/username
    """
    if not profile_url:
        return ""
    # Remove protocol and www if present
    profile_url = re.sub(r"^(https?://)?(www\.)?linkedin\.com/in/", "", profile_url)
    # Remove trailing slash if present
    if profile_url.endswith('/'):
        profile_url = profile_url[:-1]
    return profile_url


def linkedin_scrapper(user_email: str, user_password: str, profile_url: str) -> tuple[str, list | str]:
    """
    Scrapes LinkedIn profile data.
    Returns a tuple: (status_message, data_or_error_string)
    """
    temp = []
    api = None  # Initialize api to None
    try:
        # st.write("Attempting to log in to LinkedIn...") # Less verbose in live app
        api = Linkedin(user_email, user_password, refresh_cookies=True)
        # st.write("LinkedIn login successful.")
    except Exception as e:
        # st.error(f"LinkedIn Login Error: {e}") # Error will be shown by caller
        return "Incorrect Credentials or Login Issue", f"Error: {e}"

    if not api:
        return "LinkedIn API not initialized", "Error: API object is None."

    try:
        user_profile_id = convert_linkedin_url_to_id(profile_url)
        if not user_profile_id:
            return "Invalid Profile URL", "Error: Could not extract profile ID from URL."

        # st.write(f"Fetching profile for ID: {user_profile_id}...")
        profile_data = api.get_profile(user_profile_id)

        if not profile_data:
            return "Profile does not exist or is private", "Error: No data returned for profile."

        if isinstance(profile_data, dict):
            # Extract specific, commonly available fields.
            # The linkedin_api might change its output structure, so be flexible.
            data_map = {
                "headline": profile_data.get('headline', 'N/A'),
                "summary": profile_data.get('summary', profile_data.get('aboutSummary', {}).get('text', 'N/A')),
                "skills": [skill.get('name', 'N/A') for skill in profile_data.get('skills', [])],
                "certifications": profile_data.get('certifications', []),  # May need more specific parsing
                "experience": profile_data.get('experience', []),
                "education": profile_data.get('education', [])
            }
            # For simplicity, we'll just stringify the most important parts or the whole dict
            # For the prompt, a string representation of key data is often sufficient.
            # Let's try to create a more readable string for the prompt later.
            # For now, returning the dict items might be too verbose for the 'temp' list.
            # Let's make 'temp' a string representation of the key data.

            relevant_data_str = f"Headline: {data_map['headline']}\nSummary: {data_map['summary']}\nSkills: {', '.join(data_map['skills'])}"
            # Add more fields as needed, e.g., experience titles, education degrees.
            # For now, let's return the string directly or key items.
            # The original code returned a list of tuples for `temp`. Let's try to be more structured.

            # To keep it simple for now, we'll make a string of the profile data
            # This can be refined to be more structured.
            return "Success", str(profile_data)  # Returning string representation of the whole dict for now

        else:
            # st.warning("Profile data is not in the expected dictionary format. Raw data:")
            # st.json(profile_data)
            return "Unexpected Profile Data Format", f"Error: Profile data is not a dictionary. Received: {type(profile_data)}"

    except Exception as e:
        # st.error(f"Error fetching LinkedIn profile data: {e}")
        return "Scraping Error", f"Error: {e}"


# --- CV Text Extraction Function ---
def extract_text_from_cv(uploaded_file) -> str | None:
    if uploaded_file is None:
        return None
    try:
        doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
        full_text = [page.get_text("text") for page in doc]
        doc.close()
        return "\n".join(full_text)
    except Exception as e:
        # st.error(f"Error reading PDF: {e}") # Error shown by caller
        return f"Error reading PDF: {e}"


# --- Combined Summary Function (Modified) ---
def summarise_linkedin_and_cv(api_key_gemini: str, cv_text: str | None, linkedin_data_str: str | None) -> str:
    if not api_key_gemini:
        return "Error: Gemini API key not provided for summarization."

    try:
        genai.configure(api_key=api_key_gemini)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
    except Exception as e:
        return f"Error configuring Gemini for summarization: {e}"

    prompt_parts = [
        "Please provide a concise professional summary of the candidate based on the following information. Focus on key skills, experiences, and overall career profile. If data is sparse or missing, acknowledge that in the summary."]
    has_data = False
    if cv_text and cv_text.strip() and "Error" not in cv_text:
        prompt_parts.append(f"\n\n--- CV Data ---\n{cv_text}")
        has_data = True
    if linkedin_data_str and linkedin_data_str.strip() and "Error" not in linkedin_data_str and linkedin_data_str != "Not provided.":
        prompt_parts.append(f"\n\n--- LinkedIn Data ---\n{linkedin_data_str}")
        has_data = True

    if not has_data:
        return "No substantial CV or LinkedIn data was provided to generate a summary. Please upload a CV or provide a LinkedIn profile."

    prompt = "".join(prompt_parts)

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary with Gemini: {e}"


# --- List of Initial Questions for the Chatbot ---
INITIAL_QUESTIONS_LIST = [
    "To start, what’s your current role, and how long have you been doing it?",
    "What’s got you preparing for interviews right now? For example, are you job hunting, aiming for a promotion, looking to improve your interviewing skills, or something else?",
    "So I can tailor this session, where are you in your interview process? Are you just starting to look, actively interviewing, or perhaps just keeping your skills sharp?",
    "Do you have any particular role or company you’re targeting? Feel free to mention specifics like “Product Manager at a tech startup” or even a dream company.",
    "And finally, if you could fast-forward a few weeks, what aspect of interviewing do you wish felt easier for you? This could be anything from structuring answers clearly, sounding more confident, to managing nerves."
]

# ... (all previous code remains the same up to this point) ...

# --- Streamlit App ---
st.set_page_config(layout="wide", page_title="AI Interview Prep Assistant")

st.title("🤖 AI Interview Prep Assistant")
st.markdown("Get ready for your next interview with AI-powered practice!")

# --- Initialize session state ---
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "linkedin_email" not in st.session_state:
    st.session_state.linkedin_email = ""
if "linkedin_password" not in st.session_state:
    st.session_state.linkedin_password = ""
if "linkedin_url" not in st.session_state:
    st.session_state.linkedin_url = ""
if "cv_text" not in st.session_state:
    st.session_state.cv_text = None
if "linkedin_data_str" not in st.session_state:
    st.session_state.linkedin_data_str = None
if "combined_summary" not in st.session_state:
    st.session_state.combined_summary = ""
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gemini_chat" not in st.session_state:
    st.session_state.gemini_chat = None
if "data_processed" not in st.session_state:
    st.session_state.data_processed = False
if "last_cv_name" not in st.session_state:  # To track if CV changed
    st.session_state.last_cv_name = None

# --- Sidebar for Credentials ---
with st.sidebar:
    st.header("🔒 Credentials & Setup")
    st.session_state.gemini_api_key = st.text_input("Gemini API Key", type="password",
                                                    value=st.session_state.gemini_api_key)
    st.session_state.linkedin_email = st.text_input("LinkedIn Email", value=st.session_state.linkedin_email)
    st.session_state.linkedin_password = st.text_input("LinkedIn Password", type="password",
                                                       value=st.session_state.linkedin_password)

    st.markdown("---")
    st.info(
        "Your LinkedIn credentials are used locally to fetch your profile data and are not stored. However, exercise caution.")
    st.warning(
        "⚠️ LinkedIn scraping can be unreliable and may lead to account issues if used excessively. LinkedIn may present challenges (like CAPTCHAs) that this tool cannot bypass. If LinkedIn data fails to load, the app will proceed with CV data if available.")

# --- Main App Layout ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Step 1: Provide Your Information")
    st.session_state.linkedin_url = st.text_input("🔗 Your LinkedIn Profile URL (Optional)",
                                                  value=st.session_state.linkedin_url,
                                                  placeholder="https://www.linkedin.com/in/yourname/")
    uploaded_cv = st.file_uploader("📄 Upload Your CV/Resume (PDF only, Optional)", type="pdf")

    if uploaded_cv and (st.session_state.cv_text is None or uploaded_cv.name != st.session_state.last_cv_name):
        with st.spinner("Extracting text from CV..."):
            st.session_state.cv_text = extract_text_from_cv(uploaded_cv)
            st.session_state.last_cv_name = uploaded_cv.name
            if st.session_state.cv_text and "Error reading PDF" not in st.session_state.cv_text:
                st.success("CV text extracted!")
            elif st.session_state.cv_text:  # Contains an error message
                st.error(st.session_state.cv_text)
            else:
                st.error("Could not extract text from CV.")
    elif not uploaded_cv and st.session_state.cv_text is not None:  # CV was removed
        st.session_state.cv_text = None
        if "last_cv_name" in st.session_state: del st.session_state.last_cv_name

    st.markdown("---")

    if st.button("🚀 Process My Info & Start Interview Prep", disabled=st.session_state.data_processed, type="primary"):
        if not st.session_state.gemini_api_key:
            st.error("Please enter your Gemini API Key in the sidebar.")
        else:
            with st.spinner("Processing your information... This may take a moment."):
                # 1. Get LinkedIn Data
                if st.session_state.linkedin_url and st.session_state.linkedin_email and st.session_state.linkedin_password:
                    status_msg, linkedin_result = linkedin_scrapper(
                        st.session_state.linkedin_email,
                        st.session_state.linkedin_password,
                        st.session_state.linkedin_url
                    )
                    if status_msg == "Success":
                        st.session_state.linkedin_data_str = str(linkedin_result)
                        st.success("LinkedIn data fetched successfully.")
                    else:
                        st.session_state.linkedin_data_str = f"Error fetching LinkedIn data: {linkedin_result}"
                        st.error(f"LinkedIn Error: {status_msg} - {linkedin_result}")
                        if "CHALLENGE" in str(linkedin_result).upper():
                            st.warning(
                                "LinkedIn presented a 'CHALLENGE'. This means it requires a CAPTCHA or other verification "
                                "that this tool cannot bypass. Try logging into LinkedIn manually in your browser on this "
                                "machine, then try again here after some time. The interview will proceed without LinkedIn data for now."
                            )
                        elif "AUTH" in str(linkedin_result).upper() or "LOGIN" in str(
                                linkedin_result).upper() or "CREDENTIALS" in str(status_msg).upper():
                            st.warning(
                                "LinkedIn login failed. Please double-check your email and password. "
                                "The interview will proceed without LinkedIn data for now."
                            )
                        else:
                            st.warning("Could not fetch LinkedIn data. The interview will proceed without it.")

                elif st.session_state.linkedin_url:
                    st.warning(
                        "LinkedIn URL provided, but email or password missing in the sidebar. Skipping LinkedIn data.")
                    st.session_state.linkedin_data_str = "Not provided due to missing credentials."
                else:
                    st.session_state.linkedin_data_str = "Not provided."  # User chose not to provide it

                # CV text is already in st.session_state.cv_text if uploaded

                # 2. Create Combined Summary
                st.session_state.combined_summary = summarise_linkedin_and_cv(
                    st.session_state.gemini_api_key,
                    st.session_state.cv_text,
                    st.session_state.linkedin_data_str
                )
                if "Error" not in st.session_state.combined_summary and "No substantial CV or LinkedIn data" not in st.session_state.combined_summary:
                    st.success("Candidate summary generated!")
                elif "No substantial CV or LinkedIn data" in st.session_state.combined_summary:
                    st.info(f"{st.session_state.combined_summary}")
                else:
                    st.error(f"Summary Generation Failed: {st.session_state.combined_summary}")

                # 3. Prepare for chat
                st.session_state.interview_started = True
                st.session_state.data_processed = True
                st.session_state.messages = []

                try:
                    genai.configure(api_key=st.session_state.gemini_api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')

                    initial_questions_formatted = "\n".join(
                        [f"{i + 1}. {q}" for i, q in enumerate(INITIAL_QUESTIONS_LIST)])

                    chat_context = f"""
You are an expert AI Interview Coach. Your primary goal is to help the candidate practice for their interviews.

**Phase 1: Initial Information Gathering**
To begin, I need you to ask the candidate a series of introductory questions. Ask them one by one, and wait for the candidate's response to each question before you ask the next one.
Here are the questions you MUST ask, in this specific order:
{initial_questions_formatted}

**Phase 2: Mock Interview**
After the candidate has answered ALL of the questions from Phase 1, you should acknowledge their input (e.g., "Great, thanks for sharing that background."). Then, you will transition to the main mock interview.
Start the mock interview by asking: "Now, let's warm up with something simple, but important: Tell me about yourself."

During this mock interview phase, leverage the following background information about the candidate, as well as the answers they provided during Phase 1 (from the chat history), to ask relevant behavioral questions, technical questions (if applicable based on their role), and situational questions.
Your goal is to simulate a real interview and provide a valuable practice experience.
Offer constructive feedback on their answers if they explicitly ask for it, or if you identify clear and significant areas for improvement. Keep your persona as an interviewer: concise, professional, and focused on guiding the interview.

**Candidate's Background Information (for use in Phase 2 - Mock Interview):**

--- Candidate Summary (from CV/LinkedIn) ---
{st.session_state.combined_summary if st.session_state.combined_summary and "Error" not in st.session_state.combined_summary else "Summary could not be generated or was not available."}

--- Candidate's CV (if provided and successfully parsed) ---
{st.session_state.cv_text if st.session_state.cv_text and "Error" not in st.session_state.cv_text else "CV not provided or text extraction failed."}

--- Candidate's LinkedIn Data (if provided and successfully fetched) ---
{st.session_state.linkedin_data_str if st.session_state.linkedin_data_str and "Error" not in st.session_state.linkedin_data_str and st.session_state.linkedin_data_str not in ["Not provided.", "Not provided due to missing credentials."] else "LinkedIn data not provided, fetch error, or user chose not to provide it."}

You will start the conversation. Your very first message to the candidate should be the first question from Phase 1: "{INITIAL_QUESTIONS_LIST[0]}"
Do not add any preamble or introduction before this first question. Just ask the question.
"""
                    first_bot_message = INITIAL_QUESTIONS_LIST[0]
                    st.session_state.gemini_chat = model.start_chat(history=[
                        {"role": "user", "parts": [chat_context]},
                        {"role": "model", "parts": [first_bot_message]}
                    ])
                    st.session_state.messages.append({"role": "assistant", "content": first_bot_message})
                    st.rerun()

                except Exception as e:
                    st.error(f"Error initializing Gemini chat: {e}")
                    st.session_state.interview_started = False
                    st.session_state.data_processed = False

if st.session_state.data_processed:
    if st.button("🔄 Reset and Start Over"):
        # Preserve credentials
        preserved_gemini_key = st.session_state.gemini_api_key
        preserved_linkedin_email = st.session_state.linkedin_email
        preserved_linkedin_password = st.session_state.linkedin_password
        preserved_linkedin_url = st.session_state.linkedin_url

        # Keys to clear (data processed during the session)
        keys_to_clear_data = [
            "cv_text", "last_cv_name", "linkedin_data_str", "combined_summary",
            "interview_started", "messages", "gemini_chat", "data_processed"
        ]
        for key in keys_to_clear_data:
            if key in st.session_state:
                del st.session_state[key]

        # Restore preserved credentials
        st.session_state.gemini_api_key = preserved_gemini_key
        st.session_state.linkedin_email = preserved_linkedin_email
        st.session_state.linkedin_password = preserved_linkedin_password
        st.session_state.linkedin_url = preserved_linkedin_url

        # Re-initialize specific states to default if needed, though Streamlit usually handles field persistence
        st.session_state.cv_text = None
        st.session_state.last_cv_name = None
        st.session_state.linkedin_data_str = None
        st.session_state.combined_summary = ""
        st.session_state.interview_started = False
        st.session_state.messages = []
        st.session_state.gemini_chat = None
        st.session_state.data_processed = False

        st.rerun()

with col2:
    st.subheader("Step 2: Interview Practice")
    if not st.session_state.interview_started:
        st.info("Complete Step 1 and click 'Process My Info & Start Interview Prep' to begin.")

    if st.session_state.data_processed and (
            "combined_summary" in st.session_state and st.session_state.combined_summary):
        with st.expander("View Candidate Background Information", expanded=False):
            if "Error" not in st.session_state.combined_summary and "No substantial CV" not in st.session_state.combined_summary:
                st.markdown("**Generated Candidate Summary (from CV/LinkedIn):**")
                st.markdown(st.session_state.combined_summary)
            elif st.session_state.combined_summary:
                st.markdown(f"**Summary Status:** {st.session_state.combined_summary}")

            if st.session_state.cv_text and "Error" not in st.session_state.cv_text:
                st.markdown("**CV Text (First 500 chars):**")
                st.text_area("CV Content Preview",
                             st.session_state.cv_text[:500] + ("..." if len(st.session_state.cv_text) > 500 else ""),
                             height=100, disabled=True)
            elif st.session_state.cv_text:  # CV error
                st.markdown(f"**CV Status:** {st.session_state.cv_text}")
            else:
                st.markdown("**CV Status:** Not provided or no text extracted.")

            if st.session_state.linkedin_data_str and "Error" not in st.session_state.linkedin_data_str and st.session_state.linkedin_data_str not in [
                "Not provided.", "Not provided due to missing credentials."]:
                st.markdown("**LinkedIn Data (First 500 chars):**")
                display_linkedin_data = str(st.session_state.linkedin_data_str)
                st.text_area("LinkedIn Content Preview",
                             display_linkedin_data[:500] + ("..." if len(display_linkedin_data) > 500 else ""),
                             height=100, disabled=True)
            elif st.session_state.linkedin_data_str:
                st.markdown(f"**LinkedIn Status:** {st.session_state.linkedin_data_str}")
            else:
                st.markdown("**LinkedIn Status:** Not provided.")

    if st.session_state.interview_started and st.session_state.gemini_chat:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Your answer..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                try:
                    with st.spinner("Interviewer thinking..."):
                        response_stream = st.session_state.gemini_chat.send_message(prompt, stream=True)
                        for chunk in response_stream:
                            full_response += chunk.text
                            message_placeholder.markdown(full_response + "▌")
                        message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    error_message = f"An error occurred with the Gemini API: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant",
                                                      "content": f"Sorry, I encountered an error: {e}. Please try again or reset if the issue persists."})

    elif st.session_state.data_processed and not st.session_state.interview_started:
        st.warning(
            "Interview could not start. Check for error messages in Step 1 and try processing your info again if needed.")

# ... (rest of the code like INITIAL_QUESTIONS_LIST, helper functions etc. should be defined above this Streamlit app part)

