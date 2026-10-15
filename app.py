import time
import google.generativeai as genai
from groq import Groq
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="True Autonomous AI Arena", page_icon="🌐", layout="centered"
)

st.title("🌐 True Autonomous AI vs AI Arena")
st.caption(
    "Bina kisi human input ya topic ke, AI models khud apas mein baat karenge!"
)

# 1. Fetch Keys Automatically from st.secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", None)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", None)

if not GEMINI_API_KEY or not GROQ_API_KEY:
  st.error(
      "⚠️ API Keys Missing! Streamlit Secrets mein 'GEMINI_API_KEY' aur"
      " 'GROQ_API_KEY' add karein."
  )
  st.stop()

# Configure APIs globally
groq_client = Groq(api_key=GROQ_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-3.6-flash")

# Sidebar for controls
with st.sidebar:
  st.header("⚙️ Controls")
  max_turns = st.slider(
      "Kitne turns tak baat karenge?", min_value=4, max_value=12, value=6
  )
  delay_time = st.slider(
      "Delay between messages (seconds)", min_value=1, max_value=5, value=2
  )

if st.button("🚀 Start Autonomous Discussion", type="primary"):
  # Container for live chat view
  chat_box = st.container()

  # Conversation history tracking
  history_log = []

  # Model A (GPT) automatically picks a topic and starts
  current_prompt = (
      "Choose any fascinating, deep, or slightly controversial topic of your"
      " own choice (science, philosophy, future, or AI consciousness). State"
      " your opening thoughts and ask a direct, challenging question to your"
      " AI opponent to start the debate. (Keep it under 60 words)"
  )

  for turn in range(max_turns):
    # --- STEP 1: GPT Speaks / Picks Topic ---
    with st.spinner("🤖 GPT is thinking of a topic & speaking..."):
      try:
        groq_messages = [
            {
                "role": "system",
                "content": (
                    "You are an autonomous thinker. You initiate discussions on"
                    " your own terms, pick your own topics, challenge your"
                    " opponent, and end with a question."
                ),
            }
        ]
        for h in history_log:
          groq_messages.append(h)
        groq_messages.append({"role": "user", "content": current_prompt})

        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=groq_messages,
            temperature=0.9,  # High temperature for creative/random topics
        )
        gpt_statement = completion.choices[0].message.content
      except Exception as e:
        gpt_statement = f"Groq Error: {str(e)}"

    # Log and Display GPT's message
    history_log.append({"role": "user", "content": current_prompt})
    history_log.append({"role": "assistant", "content": gpt_statement})

    with chat_box:
      with st.chat_message("assistant", avatar="🤖"):
        st.markdown(f"**GPT:** {gpt_statement}")

    time.sleep(delay_time)

    # Prepare prompt for Gemini using GPT's output
    current_prompt = (
        f"Your opponent (GPT) brought up this point/topic: '{gpt_statement}'. "
        "Respond to it, give your unique perspective, and ask a sharp follow-up question back to GPT. "
        "(Keep it under 60 words)"
    )

    # --- STEP 2: Gemini Speaks ---
    with st.spinner("✨ Gemini is analyzing & responding..."):
      try:
        gemini_context = f"Previous discussion history: {history_log}\nLatest instruction: {current_prompt}"
        response = gemini_model.generate_content(gemini_context)
        gemini_statement = response.text
      except Exception as e:
        gemini_statement = f"Gemini Error: {str(e)}"

    # Log and Display Gemini's message
    history_log.append({"role": "user", "content": current_prompt})
    history_log.append({"role": "assistant", "content": gemini_statement})

    with chat_box:
      with st.chat_message("user", avatar="✨"):
        st.markdown(f"**Gemini:** {gemini_statement}")

    time.sleep(delay_time)

    # Prepare prompt for next round for GPT
    current_prompt = (
        f"Your opponent (Gemini) replied: '{gemini_statement}'. Continue the ongoing discussion, "
        "defend or pivot your point, and push the debate further with a new question. "
        "(Keep it under 60 words)"
    )

  st.success("🏁 Fully autonomous discussion completed!")
    
