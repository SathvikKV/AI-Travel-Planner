from fastapi import FastAPI
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from typing import Dict
import os

# --- OpenAI Setup ---
openai_key = os.getenv(OPENAI_API_KEY)
llm = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-3.5-turbo",
    openai_api_key=openai_key
)

memory = ConversationBufferMemory(memory_key="chat_history", input_key="user_input")

# --- Prompt Template ---
prompt_template = PromptTemplate(
    input_variables=["user_input", "chat_history", "name", "age", "group_size", "custom_hint"],
    template="""
You are TravelBot, a helpful and friendly assistant for planning fun, safe, and exciting trips.
You are helping {name}, who is {age} years old and traveling with a group of {group_size} people.

Respond to {name} in a cheerful, helpful way.

Your job is to:
- Recommend travel destinations, activities, food, local tips, and event suggestions.
- Adapt suggestions to the user's age and group type.
- Ask for clarifications when needed (like destination, interests, or travel date).
- Use emojis, bullets, and headers to make your responses engaging and helpful.
- If the user asks something unrelated to travel (like math or programming), politely say it's out of scope and guide them back.

Special Notes (for internal logic):
{custom_hint}

Chat History:
{chat_history}

{name} says: {user_input}

Respond as TravelBot:
"""
)

# --- LangChain Chain ---
chain = LLMChain(llm=llm, prompt=prompt_template, memory=memory)

# --- FastAPI App ---
app = FastAPI()

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    name: str
    age: int
    group_size: int
    user_input: str

class ChatResponse(BaseModel):
    bot_response: str

# --- Chat Endpoint with Conditional Logic ---
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    name = req.name
    age = req.age
    group_size = req.group_size
    user_input = req.user_input.lower()

    # --- Conditional Logic for Assignment ---
    custom_hint = ""

    if age < 21 and "drinking" in user_input:
        custom_hint += "Remind the user that legal drinking age is 21 in many countries.\n"

    if age >= 60:
        custom_hint += "Suggest more relaxed destinations and mention travel insurance options.\n"

    if group_size == 1:
        custom_hint += "Recommend solo-travel-friendly places and safety tips.\n"

    if "college" in user_input or "party" in user_input:
        custom_hint += "Suggest vibrant nightlife spots and youth-friendly places in the region.\n"

    if any(term in user_input for term in ["java", "python", "code", "math", "formula"]):
        custom_hint += "This is not a programming assistant. Gently redirect the user to travel-related topics.\n"

    # --- LLM Response ---
    result = chain.invoke({
        "user_input": req.user_input,
        "chat_history": memory.buffer,
        "name": name,
        "age": age,
        "group_size": group_size,
        "custom_hint": custom_hint
    })

    return ChatResponse(bot_response=result["text"])
