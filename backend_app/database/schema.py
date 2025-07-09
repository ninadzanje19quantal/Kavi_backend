import uuid
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date, Boolean, DECIMAL, JSON, ARRAY, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, TEXT, TIMESTAMP
from datetime import datetime

password = "u3KrUSJDaEgJqZ89"

DATABASE_URL = f"postgresql://postgres.tgsstxvgndqcwwiraxdb:{password}@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


class Profile(Base):  # Existing table
    __tablename__ = 'profiles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255)) | None
    avatar_url = Column(String(255)) | None
    linkedin_data = Column(String(1000)) | None
    linkedin_url = Column(String(100)) | None
    cv_data = Column(String(1000)) | None
    cv_path = Column(String(100)) | None
    # Assuming this links to Supabase auth.users, you might have a direct auth_id column or similar.  Adapt as needed.
    auth_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id')) # Example of foreign key to auth.users

def add_user(auth_ID: str,
             name: str,
             email: str,
             linkedin_data: str,
             linkedin_url: str,
             cv_dta: str):
    user = Profile(auth_id=auth_ID,
                   full_name=name,
                   email=email,
                   linkedin_data=linkedin_data,
                   linkedin_url=linkedin_url,
                   cv_data=cv_dta)
    session.add_all([user])
    session.commit()
#add_user(,"Ninad", "ninadzanje@mail.com", "ninad-zanje", "aaaaaa")
def get_user_by_id(user_id):
    user_profile = session.query(Profile).filter_by(id=user_id).all()
    for user in user_profile:
        print(user.full_name)

def get_users():
    pass

def delete_user(user_id):
    user_profile = session.query(Profile).filter_by(id=user_id).all()
    session.delete(user_profile)
    session.commit()

def update_user():
    pass


class AgentStory(Base):  # Existing table
    __tablename__ = 'agent_stories'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    conversation_id = Column(TEXT)  # Or UUID, depending on your actual conversation ID format
    story_text = Column(TEXT)
    analysis_results = Column(JSONB)  # Store AI analysis
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Profile", backref="agent_stories")

class CustomPracticeQuestion(Base):  # Existing table
    __tablename__ = 'custom_practice_questions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    question_text = Column(TEXT, nullable=False)
    category = Column(String(255))
    tags = Column(ARRAY(TEXT))
    attempt_history = Column(JSONB)  # Store attempt data
    status = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Profile", backref="custom_practice_questions")

class ChatbotConversation(Base):
    # Existing table
    __tablename__ = 'chatbot_conversation'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    conversation_metadata = Column(JSONB)
    conversation_steps = Column(JSONB)  # Store the sequential flow
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Profile", backref="chatbot_conversations")

class UserOnboardingData(Base):

    __tablename__ = 'user_onboarding_data'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    linkedin_url = Column(TEXT)
    linkedin_data = Column(JSONB)
    cv_data = Column(JSONB)
    goals = Column(TEXT)
    target_companies = Column(ARRAY(TEXT))
    target_roles = Column(ARRAY(TEXT))
    experience_level = Column(TEXT)
    industry = Column(TEXT)
    onboarding_completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Profile", backref="onboarding_data")  # Backref for easy access from User model

class UserProgressTracking(Base):

    __tablename__ = 'user_progress_tracking'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    skill_category = Column(TEXT)
    current_score = Column(Integer)
    previous_score = Column(Integer)
    sessions_completed = Column(Integer)
    last_session_date = Column(Date)
    improvement_points = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Profile", backref="progress_tracking")

class PracticeSession(Base):

    __tablename__ = 'practice_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    session_type = Column(TEXT)
    agent_id = Column(TEXT)  # ElevenLabs agent identifier
    conversation_id = Column(TEXT)  # Links to ElevenLabs conversation
    duration_seconds = Column(Integer)
    status = Column(TEXT)  # completed, abandoned, in_progress
    score = Column(Integer)
    feedback = Column(TEXT)  # AI-generated feedback
    strengths = Column(ARRAY(TEXT))
    areas_for_improvement = Column(ARRAY(TEXT))
    session_metadata = Column(JSONB)
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Profile", backref="practice_sessions")

class VoiceConversationTranscript(Base):

    __tablename__ = 'voice_conversation_transcripts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_session_id = Column(UUID(as_uuid=True), ForeignKey('practice_sessions.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    elevenlabs_conversation_id = Column(TEXT)
    transcript_data = Column(JSONB)  # Full conversation transcript
    speaker_analysis = Column(JSONB)  # Speaking pace, pauses, confidence metrics
    question_response_pairs = Column(JSONB)  # Structured Q&A data
    sentiment_analysis = Column(JSONB)  # Emotional tone analysis
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    practice_session = relationship("PracticeSession", backref="voice_conversation_transcripts")
    user = relationship("Profile")

class InterviewQuestionLibrary(Base):

    __tablename__ = 'interview_questions_library'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(TEXT)  # Behavioral, Technical, Case Study, etc.
    subcategory = Column(TEXT)  # Leadership, Problem-solving, etc.
    question_text = Column(TEXT)
    difficulty_level = Column(TEXT)  # Beginner, Intermediate, Advanced
    estimated_duration_minutes = Column(Integer)
    tags = Column(ARRAY(TEXT))
    target_roles = Column(ARRAY(TEXT))
    target_industries = Column(ARRAY(TEXT))
    sample_answer = Column(TEXT)
    evaluation_criteria = Column(JSONB)
    is_active = Column(Boolean)
    created_by = Column(TEXT)  # system or admin
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class LearningPath(Base):
    __tablename__ = 'learning_paths'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    path_name = Column(TEXT)  # "Senior Product Manager Track"
    description = Column(TEXT)
    total_sessions = Column(Integer)
    completed_sessions = Column(Integer)
    current_session = Column(Integer)
    estimated_completion_days = Column(Integer)
    is_active = Column(Boolean)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Profile", backref="learning_paths")

class LearningPathSession(Base):
    __tablename__ = 'learning_path_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learning_path_id = Column(UUID(as_uuid=True), ForeignKey('learning_paths.id'))
    session_order = Column(Integer)
    session_title = Column(TEXT)
    session_description = Column(TEXT)
    question_ids = Column(ARRAY(UUID(as_uuid=True)))  # Array of question IDs (from interview_questions_library)
    required_agent_id = Column(TEXT)  # Specific ElevenLabs agent
    prerequisites = Column(ARRAY(TEXT))
    learning_objectives = Column(ARRAY(TEXT))
    is_locked = Column(Boolean)
    unlock_conditions = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    learning_path = relationship("LearningPath", backref="sessions")

class UserAchievement(Base):
    __tablename__ = 'user_achievements'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    achievement_type = Column(TEXT)  # streak, score, completion, etc.
    achievement_name = Column(TEXT)  # "7 Day Streak", "Communication Expert"
    description = Column(TEXT)
    points_earned = Column(Integer)
    badge_icon = Column(TEXT)  # URL or identifier
    unlocked_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("Profile", backref="achievements")

class PracticeStreak(Base):
    __tablename__ = 'practice_streaks'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    current_streak = Column(Integer)
    longest_streak = Column(Integer)
    last_practice_date = Column(Date)
    streak_started_at = Column(Date)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Profile", backref="practice_streaks")

class SessionFeedback(Base):
    __tablename__ = 'session_feedback'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_session_id = Column(UUID(as_uuid=True), ForeignKey('practice_sessions.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    ai_feedback = Column(TEXT)
    improvement_suggestions = Column(ARRAY(TEXT))
    strengths_identified = Column(ARRAY(TEXT))
    speaking_metrics = Column(JSONB)  # Pace, volume, clarity scores
    content_quality_score = Column(Integer)
    delivery_score = Column(Integer)
    overall_score = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    practice_session = relationship("PracticeSession", backref="feedback")
    user = relationship("Profile")

class UserGoal(Base):
    __tablename__ = 'user_goals'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    goal_type = Column(TEXT)  # interview_prep, skill_improvement, confidence
    goal_description = Column(TEXT)
    target_date = Column(Date)
    current_progress = Column(Integer)  # Percentage
    milestones = Column(JSONB)  # Checkpoints and achievements
    is_completed = Column(Boolean)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Profile", backref="goals")

class CompanyProfile(Base):
    __tablename__ = 'company_profiles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(TEXT)
    industry = Column(TEXT)
    company_size = Column(TEXT)
    culture_description = Column(TEXT)
    interview_process = Column(JSONB)  # Typical interview stages
    common_questions = Column(ARRAY(TEXT))
    glassdoor_rating = Column(DECIMAL)
    website_url = Column(TEXT)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class RoleProfile(Base):
    __tablename__ = 'role_profiles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_title = Column(TEXT)
    role_level = Column(TEXT)  # Junior, Senior, Principal, etc.
    department = Column(TEXT)  # Product, Engineering, Marketing
    key_skills = Column(ARRAY(TEXT))
    typical_questions = Column(ARRAY(UUID(as_uuid=True)))  # References to interview_questions_library (array of UUIDs)
    salary_range = Column(JSONB)
    growth_trajectory = Column(TEXT)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class ElevenlabsIntegrationLog(Base):
    __tablename__ = 'elevenlabs_integration_log'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    conversation_id = Column(TEXT)
    agent_id = Column(TEXT)
    session_duration_seconds = Column(Integer)
    api_usage_tokens = Column(Integer)
    error_log = Column(TEXT)
    status = Column(TEXT)  # success, error, timeout
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("Profile")

class UserPreference(Base):
    __tablename__ = 'user_preferences'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    preferred_session_duration = Column(Integer)  # Minutes
    notification_settings = Column(JSONB)
    voice_settings = Column(JSONB)  # Speed, accent preferences
    difficulty_preference = Column(TEXT)
    practice_frequency_goal = Column(Integer)  # Sessions per week
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Profile", backref="preferences")



"""# Example Usage (Connecting and Creating Tables)
if __name__ == '__main__':
    engine = create_engine('postgresql://user:password@host:port/database')  # Replace with your actual database URL
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Example: Creating a new user profile
    new_profile = Profile(email='test@example.com', full_name='Test User')
    session.add(new_profile)
    session.commit()

    print("Tables created and example data added.")
    session.close()"""