import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

# --- Initialize Session State ---
if "name" not in st.session_state:
    st.session_state.name = ""
if "age" not in st.session_state:
    st.session_state.age = None
if "group_size" not in st.session_state:
    st.session_state.group_size = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar Controls ---
with st.sidebar:
    st.title("🗺️ Travel Planner Setup")
    st.markdown("Please enter your details to get personalized travel suggestions:")

    st.session_state.name = st.text_input("👤 Your Name:", value=st.session_state.name)
    st.session_state.age = st.number_input("🎂 Your Age:", min_value=1, max_value=120, step=1, value=st.session_state.age or 25)
    st.session_state.group_size = st.number_input("🧑‍🤝‍🧑 Group Size:", min_value=1, step=1, value=st.session_state.group_size or 2)

    st.markdown("---")
    st.markdown("💡 **Example Prompts**")
    st.markdown("- I want to visit Europe in summer")
    st.markdown("- Best beaches for spring break?")
    st.markdown("- Suggest a trip with my college friends")
    st.markdown("---")
    st.markdown("🌍 Built with LangChain + FastAPI + Streamlit")

# --- Header ---
st.title("🧳 Travel Planner Chatbot")

# --- Check for required info ---
if not st.session_state.name or st.session_state.age is None or st.session_state.group_size is None:
    st.info("Please enter your name, age, and group size in the sidebar to begin.")
    st.stop()

# --- Initial Welcome ---
if not st.session_state.messages:
    st.session_state.messages.append(("🤖", f"Hi {st.session_state.name}! Where would you like to go?"))

# --- Display Chat History ---
for sender, message in st.session_state.messages:
    with st.chat_message("user" if sender == "🧍" else "assistant"):
        st.markdown(message)

# --- Input Box ---
user_input = st.chat_input("Where are you planning to travel?")
if user_input:
    st.session_state.messages.append(("🧍", user_input))

    payload = {
        "name": st.session_state.name,
        "age": st.session_state.age,
        "group_size": st.session_state.group_size,
        "user_input": user_input
    }

    try:
        res = requests.post(API_URL, json=payload)
        if res.status_code == 200:
            result = res.json()
            bot_reply = result.get("bot_response", "Sorry, something went wrong.")
        else:
            bot_reply = "⚠️ Error: API failed to respond properly."
    except Exception as e:
        bot_reply = f"❌ Exception: {str(e)}"

    st.session_state.messages.append(("🤖", bot_reply))
    st.rerun()
