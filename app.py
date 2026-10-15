import random
import time
import google.generativeai as genai
from groq import Groq
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Autonomous Theory Builder", page_icon="🧪", layout="centered"
)

st.title("🧪 Autonomous AI Theory & Co-Creation Arena")
st.caption(
    "Aap ek topic dein; GPT aur Gemini aapas mein milkar ek nayi theory ya"
    " research framework taiyar karenge!"
)

# ---------------------------------------------------------
# DYNAMIC MULTI-KEY GEMINI MANAGEMENT (1 to Infinity Support)
# ---------------------------------------------------------
# Secrets se saari available Gemini/Google API keys ko extract karna
gemini_keys = []

# Method 1: Check for indexed keys like GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.
for key_name in st.secrets:
  if key_name.startswith("GEMINI_API_KEY") or key_name.startswith(
      "GOOGLE_API_KEY"
  ):
    val = st.secrets[key_name]
    if val and val not in gemini_keys:
      gemini_keys.append(val)

# Fallback: Agar koi single key di ho
if not gemini_keys:
  single_key = st.secrets.get("GEMINI_API_KEY", None) or st.secrets.get(
      "GOOGLE_API_KEY", None
  )
  if single_key:
    gemini_keys.append(single_key)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", None)

if not gemini_keys or not GROQ_API_KEY:
  st.error(
      "⚠️ API Keys Missing! Streamlit Secrets mein 'GEMINI_API_KEY' (ya"
      " GEMINI_API_KEY_1, _2...) aur 'GROQ_API_KEY' add karein."
  )
  st.stop()


# Helper function to get a working Gemini model with automatic key rotation on failure
def generate_gemini_response(prompt_text):
  global gemini_keys
  # Try keys in rotation or random order to bypass quota exhaustion
  tried_keys = 0
  max_tries = len(gemini_keys)

  while tried_keys < max_tries:
    # Pick the current key (can rotate or pick sequentially)
    current_key = gemini_keys[0]
    try:
      genai.configure(api_key=current_key)
      model = genai.GenerativeModel("gemini-3.6-flash")
      response = model.generate_content(prompt_text)
      return response.text
    except Exception as e:
      err_str = str(e)
      # Agar quota exhaust ya rate limit ho toh key ko rotate karke end mein bhej do
      if "quota" in err_str.lower() or "rate limit" in err_str.lower():
        gemini_keys.append(gemini_keys.pop(0))  # Rotate list
        tried_keys += 1
      else:
        return f"Gemini Error: {err_str}"

  return (
      "Gemini Error: All available Gemini API keys have exhausted their"
      " quotas."
  )


# Configure Groq client globally
groq_client = Groq(api_key=GROQ_API_KEY)

# Sidebar for controls
with st.sidebar:
  st.header("⚙️ Theory Settings")
  st.info(f"🔑 Loaded Gemini Keys Pool: {len(gemini_keys)} Active Keys")
  max_turns = st.slider(
      "Collaboration Steps (Turns)", min_value=3, max_value=10, value=6
  )
  delay_time = st.slider(
      "Pacing Delay (seconds)", min_value=1, max_value=5, value=2
  )

# User Topic Input
theory_topic = st.text_input(
    "🎯 Kis topic ya problem par Theory banwani hai?",
    (
        "A mathematical and structural framework for achieving true Artificial"
        " General Intelligence (AGI) consciousness."
    ),
)

if st.button("🚀 Start Theory Co-Creation", type="primary"):
  if not theory_topic:
    st.warning("⚠️ Pehle koi topic toh enter karein!")
  else:
    # Container for live display
    chat_box = st.container()

    # Session log for theory building
    theory_log = []

    # Initial prompt for GPT to lay down the first foundational pillar of the theory
    current_prompt = (
        f"We are co-creating a formal theory, research framework, or structural model on this topic: '{theory_topic}'. "
        "As the lead theoretician (GPT), write the foundational hypothesis, core principles, and the first pillar of this theory. "
        "Keep it structured, academic, and insightful (under 100 words)."
    )

    for turn in range(max_turns):
      # --- STEP 1: GPT (Lead Theorist) Contribution ---
      with st.spinner("🤖 GPT is formulating theory components..."):
        try:
          groq_messages = [
              {
                  "role": "system",
                  "content": (
                      "You are an expert Lead Theorist and Researcher. Your goal"
                      " is to build, expand, and structure a groundbreaking"
                      " theory collaboratively with your co-researcher"
                      " (Gemini)."
                  ),
              }
          ]
          for h in theory_log:
            groq_messages.append(h)
          groq_messages.append({"role": "user", "content": current_prompt})

          completion = groq_client.chat.completions.create(
              model="openai/gpt-oss-20b",
              messages=groq_messages,
              temperature=0.7,
          )
          gpt_output = completion.choices[0].message.content
        except Exception as e:
          gpt_output = f"Groq Error: {str(e)}"

      theory_log.append({"role": "user", "content": current_prompt})
      theory_log.append({"role": "assistant", "content": gpt_output})

      with chat_box:
        with st.chat_message("assistant", avatar="🧬"):
          st.markdown(f"**GPT (Theorist):**\n\n{gpt_output}")

      time.sleep(delay_time)

      # Prepare prompt for Gemini to critique, expand, or add the next section of the theory
      current_prompt = (
          f"Your co-researcher (GPT) proposed this theoretical addition:\n'{gpt_output}'.\n"
          "Review this framework, critique any limitations, expand the next logical layer or mathematical/logical architecture of the theory, "
          "and push the model further. Keep it structured and academic (under 100 words)."
      )

      # --- STEP 2: Gemini (Co-Researcher & Critic) Contribution with Multi-Key Rotation ---
      with st.spinner(
          "✨ Gemini is expanding & refining the theory (Auto-rotating keys if"
          " needed)..."
      ):
        gemini_context = f"Ongoing Theory Development History: {theory_log}\nLatest instruction: {current_prompt}"
        gemini_output = generate_gemini_response(gemini_context)

      theory_log.append({"role": "user", "content": current_prompt})
      theory_log.append({"role": "assistant", "content": gemini_output})

      with chat_box:
        with st.chat_message("user", avatar="🔬"):
          st.markdown(f"**Gemini (Co-Developer):**\n\n{gemini_output}")

      time.sleep(delay_time)

      # Prepare prompt for next round for GPT
      current_prompt = (
          f"Based on Gemini's refinement:\n'{gemini_output}',\n"
          "Synthesize these ideas, resolve any counter-arguments, and draft the next advanced section or final conclusion of our theory. "
          "(Keep it under 100 words)"
      )

    st.success("🎉 Theory Co-Creation Completed Successfully!")
    
