from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import hashlib
import json
import re
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize LLM Chat
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Mental Health Crisis Helplines in India
CRISIS_HELPLINES = {
    "KIRAN": {
        "name": "KIRAN Mental Health Rehabilitation Helpline",
        "number": "1800-599-0019",
        "hours": "24/7",
        "description": "Government of India mental health helpline"
    },
    "Vandrevala": {
        "name": "Vandrevala Foundation",
        "number": "9999-666-555",
        "hours": "24/7",
        "description": "Free mental health support and crisis intervention"
    },
    "Sneha": {
        "name": "SNEHA Suicide Prevention Centre",
        "number": "044-2464-0050",
        "hours": "24/7",
        "description": "Chennai-based suicide prevention and mental health support"
    },
    "Sumaitri": {
        "name": "Sumaitri",
        "number": "011-2338-9090",
        "hours": "24/7",
        "description": "Delhi-based emotional support and suicide prevention"
    }
}

# Crisis detection keywords
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die", "self harm", "cutting", 
    "hopeless", "worthless", "can't go on", "no way out", "end it all", "hurt myself",
    "overdose", "jump off", "hang myself", "razor", "pills", "bridge"
]

# Define Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    message: str
    response: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_crisis: bool = False
    data_hash: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    id: str
    response: str
    is_crisis: bool
    helplines: Optional[dict] = None
    timestamp: datetime

class WellnessResource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    category: str
    tags: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

def create_data_hash(data: str) -> str:
    """Create a blockchain-style hash for data integrity"""
    return hashlib.sha256(data.encode()).hexdigest()

def detect_crisis(message: str) -> bool:
    """Detect potential mental health crisis in user message"""
    message_lower = message.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            return True
    return False

async def get_ai_response(message: str, session_id: str, is_crisis: bool = False) -> str:
    """Get AI response with mental health context"""
    try:
        system_message = """You are a compassionate, culturally-sensitive mental health support AI designed specifically for Indian youth. 

IMPORTANT GUIDELINES:
- You are NOT a replacement for professional therapy or medical treatment
- Always emphasize that you provide supportive conversation, not professional medical advice
- Be empathetic, non-judgmental, and culturally aware of Indian contexts
- Use gentle, encouraging language
- Acknowledge academic and social pressures common in Indian society
- Be sensitive to family dynamics and cultural expectations
- If discussing serious mental health concerns, gently suggest professional help

CRISIS PROTOCOL:
- If the user expresses suicidal thoughts or self-harm, acknowledge their pain with empathy
- Remind them that their life has value and that help is available
- Direct them to professional crisis helplines
- Stay calm and supportive

Always respond in a warm, understanding tone that makes the user feel heard and supported."""

        if is_crisis:
            system_message += "\n\nCRISIS ALERT: This user may be in crisis. Respond with immediate empathy and care while directing them to professional help."

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-5")

        user_message = UserMessage(text=message)
        response = await chat.send_message(user_message)
        
        return response
    except Exception as e:
        logging.error(f"AI response error: {e}")
        return "I'm here to listen and support you. While I'm having technical difficulties right now, please know that what you're feeling is valid. If you're in crisis, please reach out to a mental health helpline immediately."

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Mental Wellness AI API for Indian Youth"}

@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Main chat endpoint with crisis detection"""
    try:
        # Detect crisis
        is_crisis = detect_crisis(request.message)
        
        # Get AI response
        ai_response = await get_ai_response(request.message, request.session_id, is_crisis)
        
        # Create secure hash for blockchain-style data integrity
        data_to_hash = f"{request.session_id}:{request.message}:{ai_response}"
        data_hash = create_data_hash(data_to_hash)
        
        # Create chat record
        chat_record = ChatMessage(
            session_id=request.session_id,
            message=request.message,
            response=ai_response,
            is_crisis=is_crisis,
            data_hash=data_hash
        )
        
        # Store in database with encryption hash
        chat_dict = chat_record.dict()
        chat_dict['timestamp'] = chat_dict['timestamp'].isoformat()
        await db.chat_messages.insert_one(chat_dict)
        
        # Prepare response
        response = ChatResponse(
            id=chat_record.id,
            response=ai_response,
            is_crisis=is_crisis,
            timestamp=chat_record.timestamp
        )
        
        # Add helplines if crisis detected
        if is_crisis:
            response.helplines = CRISIS_HELPLINES
            
        return response
        
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Unable to process chat request")

@api_router.get("/helplines")
async def get_helplines():
    """Get mental health crisis helplines"""
    return {"helplines": CRISIS_HELPLINES}

@api_router.get("/wellness-resources")
async def get_wellness_resources():
    """Get mental wellness resources and tips"""
    resources = [
        {
            "id": str(uuid.uuid4()),
            "title": "Deep Breathing Exercise",
            "content": "Practice 4-7-8 breathing: Inhale for 4 counts, hold for 7, exhale for 8. This helps calm your nervous system and reduce anxiety.",
            "category": "breathing",
            "tags": ["anxiety", "stress", "quick-relief"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Mindful Grounding Technique",
            "content": "Use the 5-4-3-2-1 technique: Name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, 1 thing you can taste.",
            "category": "mindfulness",
            "tags": ["grounding", "anxiety", "present-moment"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Managing Academic Pressure",
            "content": "Remember that your worth isn't defined by grades. Break large tasks into smaller ones, celebrate small wins, and don't hesitate to ask for help when needed.",
            "category": "academic",
            "tags": ["study-stress", "exam-anxiety", "self-worth"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Dealing with Family Expectations",
            "content": "It's natural to want to make your family proud, but your mental health comes first. Communicate openly about your struggles and set healthy boundaries.",
            "category": "family",
            "tags": ["family-pressure", "boundaries", "communication"]
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Building Self-Compassion",
            "content": "Treat yourself with the same kindness you'd show a good friend. Practice positive self-talk and remember that everyone makes mistakes - it's part of being human.",
            "category": "self-care",
            "tags": ["self-compassion", "self-talk", "emotional-support"]
        }
    ]
    
    return {"resources": resources}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    status_dict = status_obj.dict()
    status_dict['timestamp'] = status_dict['timestamp'].isoformat()
    _ = await db.status_checks.insert_one(status_dict)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    for check in status_checks:
        if isinstance(check.get('timestamp'), str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()