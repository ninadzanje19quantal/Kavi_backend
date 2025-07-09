import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    create_engine,
    Column,
    TIMESTAMP,
    ForeignKey,
    String
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB

# --- Boilerplate Setup (You would have this in your app's DB setup) ---

# 1. Define a Base
Base = declarative_base()

# 2. Define the dependent table 'profiles' for the relationship to work
class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ... other profile columns like email, name, etc.

# 3. Your ChatbotConversation class
class ChatbotConversation(Base):
    __tablename__ = 'chatbot_conversation'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)
    conversation_metadata = Column(JSONB)
    conversation_steps = Column(JSONB)  # Store the sequential flow
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Profile", back_populates="chatbot_conversations")

# Add the back-reference to the Profile class
Profile.chatbot_conversations = relationship("ChatbotConversation", back_populates="user", cascade="all, delete-orphan")

# --- Database Session Setup (Example) ---
# In a real app, this would be configured centrally.
# Using in-memory SQLite for this example to make it runnable.
# For PostgreSQL, you'd use: "postgresql://user:password@host/dbname"
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the in-memory database
Base.metadata.create_all(bind=engine)

#CREATE
def create_conversation(
    db: Session,
    user_id: uuid.UUID,
    metadata: Optional[Dict[str, Any]] = None,
    steps: Optional[List[Dict[str, Any]]] = None
) -> ChatbotConversation:
    """
    Creates a new chatbot conversation.

    Args:
        db: The SQLAlchemy database session.
        user_id: The UUID of the user starting the conversation.
        metadata: A JSON-compatible dictionary for metadata.
        steps: A JSON-compatible list of dictionaries representing conversation steps.

    Returns:
        The newly created ChatbotConversation object.
    """
    new_conversation = ChatbotConversation(
        user_id=user_id,
        conversation_metadata=metadata or {},
        conversation_steps=steps or []
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)  # Refresh to get DB-defaults like id, created_at
    return new_conversation

#READ

def get_conversation_by_id(db: Session, conversation_id: uuid.UUID) -> Optional[ChatbotConversation]:
    """
    Retrieves a single conversation by its unique ID.

    Args:
        db: The SQLAlchemy database session.
        conversation_id: The UUID of the conversation to retrieve.

    Returns:
        The ChatbotConversation object if found, otherwise None.
    """
    return db.query(ChatbotConversation).filter(ChatbotConversation.id == conversation_id).first()


def get_conversations_by_user(
    db: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> List[ChatbotConversation]:
    """
    Retrieves all conversations for a specific user, with pagination.

    Args:
        db: The SQLAlchemy database session.
        user_id: The UUID of the user whose conversations to retrieve.
        skip: The number of records to skip (for pagination).
        limit: The maximum number of records to return (for pagination).

    Returns:
        A list of ChatbotConversation objects.
    """
    return (
        db.query(ChatbotConversation)
        .filter(ChatbotConversation.user_id == user_id)
        .order_by(ChatbotConversation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

#UPDATE
def update_conversation(
        db: Session,
        conversation_id: uuid.UUID,
        update_data: Dict[str, Any]
) -> Optional[ChatbotConversation]:
    """
    Updates an existing chatbot conversation.

    Args:
        db: The SQLAlchemy database session.
        conversation_id: The UUID of the conversation to update.
        update_data: A dictionary with the fields to update.
                     e.g., {"conversation_steps": new_steps}

    Returns:
        The updated ChatbotConversation object if found, otherwise None.
    """
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        return None

    # Update fields from the provided dictionary
    for key, value in update_data.items():
        if hasattr(conversation, key):
            setattr(conversation, key, value)

    # The 'updated_at' field will be updated automatically by the database
    # due to the 'onupdate' parameter in the Column definition.
    db.commit()
    db.refresh(conversation)
    return conversation

#DELETE
def delete_conversation(db: Session, conversation_id: uuid.UUID) -> bool:
    """
    Deletes a conversation by its ID.

    Args:
        db: The SQLAlchemy database session.
        conversation_id: The UUID of the conversation to delete.

    Returns:
        True if the conversation was deleted, False if it was not found.
    """
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation:
        return False

    db.delete(conversation)
    db.commit()
    return True

###########################################################################################
###########################################################################################
###########################################################################################
from schema import UserOnboardingData

#CREATE
def create_onboarding_data(
    db: Session,
    user_id: uuid.UUID,
    data: Dict[str, Any]
) -> UserOnboardingData:
    """
    Creates a new user onboarding data record.

    Args:
        db: The SQLAlchemy database session.
        user_id: The UUID of the user.
        data: A dictionary containing onboarding data fields like 'linkedin_url',
              'goals', 'target_companies', etc.

    Returns:
        The newly created UserOnboardingData object.
    """
    new_onboarding_data = UserOnboardingData(
        user_id=user_id,
        **data
    )
    db.add(new_onboarding_data)
    db.commit()
    db.refresh(new_onboarding_data)
    return new_onboarding_data

#READ
def get_onboarding_data_by_user_id(db: Session, user_id: uuid.UUID) -> Optional[UserOnboardingData]:
    """
    Retrieves the onboarding data for a specific user.

    Args:
        db: The SQLAlchemy database session.
        user_id: The UUID of the user.

    Returns:
        The UserOnboardingData object if found, otherwise None.
    """
    return db.query(UserOnboardingData).filter(UserOnboardingData.user_id == user_id).first()


def get_onboarding_data_by_id(db: Session, data_id: uuid.UUID) -> Optional[UserOnboardingData]:
    """
    Retrieves an onboarding data record by its unique ID.

    Args:
        db: The SQLAlchemy database session.
        data_id: The UUID of the onboarding data record.

    Returns:
        The UserOnboardingData object if found, otherwise None.
    """
    return db.query(UserOnboardingData).filter(UserOnboardingData.id == data_id).first()

#UPDATE
def update_onboarding_data(
        db: Session,
        data_id: uuid.UUID,
        update_data: Dict[str, Any]
) -> Optional[UserOnboardingData]:
    """
    Updates an existing user onboarding data record.

    Args:
        db: The SQLAlchemy database session.
        data_id: The UUID of the onboarding data record to update.
        update_data: A dictionary with the fields to update.

    Returns:
        The updated UserOnboardingData object if found, otherwise None.
    """
    db_onboarding_data = get_onboarding_data_by_id(db, data_id)
    if not db_onboarding_data:
        return None

    for key, value in update_data.items():
        if hasattr(db_onboarding_data, key):
            setattr(db_onboarding_data, key, value)

    # The 'updated_at' field is handled automatically by the 'onupdate' parameter.
    db.commit()
    db.refresh(db_onboarding_data)
    return db_onboarding_data

#DELETE

def delete_onboarding_data(db: Session, data_id: uuid.UUID) -> bool:
    """
    Deletes a user onboarding data record by its ID.

    Args:
        db: The SQLAlchemy database session.
        data_id: The UUID of the record to delete.

    Returns:
        True if the record was deleted, False if it was not found.
    """
    db_onboarding_data = get_onboarding_data_by_id(db, data_id)
    if not db_onboarding_data:
        return False

    db.delete(db_onboarding_data)
    db.commit()
    return True