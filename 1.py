import streamlit as st
from google import genai
from google.genai import types

# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="Hameed's AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ================= GEMINI API & CLIENT =================

# Direct API Key bina kisi secrets ke jhanjhat ke
API_KEY = "AIzaSyAF44ttY0522PsB6D1gX6oJ_M4Eafdsh_Q"

# Naye SDK client ko initialize kiya
client = genai.Client(api_key=API_KEY)

# ================= CHAT FUNCTION (STREAMING ON) =================

def chat_with_gemini_stream(prompt, history, system_instruction):
    # send_message_stream ke liye chat object banaya
    chat = client.chats.create(
        model="gemini-2.5-flash",
        history=history,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )
    
    # Yeh pure response ke bajaye chunks (tukre) return karega
    response_stream = chat.send_message_stream(prompt)
    for chunk in response_stream:
        yield chunk.text

# ================= CSS STYLING =================

st.markdown("""
<style>

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.stApp{
    background:
        radial-gradient(circle at top left,#172554 0%,transparent 30%),
        radial-gradient(circle at bottom right,#581c87 0%,transparent 30%),
        linear-gradient(135deg,#020617,#0f172a);

    color:white;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background:rgba(10,15,30,0.85);
    backdrop-filter:blur(20px);
}

/* Title */
.main-title{
    font-size:55px;
    font-weight:800;
    background:linear-gradient(90deg,#ffffff,#c084fc,#7c3aed);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    margin-bottom:5px;
}

/* Subtitle */
.subtitle{
    color:#94a3b8;
    margin-bottom:30px;
}

/* Chat Messages */
.stChatMessage{
    background:rgba(17,24,39,0.65);
    border:1px solid rgba(255,255,255,0.05);
    border-radius:22px;
    padding:15px;
    margin-bottom:15px;
    backdrop-filter:blur(16px);
}

/* Input Box */
.stChatInput input{
    background:rgba(15,23,42,0.95)!important;
    color:white!important;
    border-radius:40px!important;
    border:1px solid rgba(168,85,247,0.35)!important;
    padding:16px!important;
}

/* Sidebar Buttons */
.stButton button{
    background:linear-gradient(90deg,#7c3aed,#2563eb);
    color:white;
    border:none;
    border-radius:14px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================

with st.sidebar:
    st.markdown("## ⚙ SYSTEM CONTROLS")

    persona = st.selectbox(
        "Select Active Persona:",
        [
            "Coding Expert",
            "Business Consultant",
            "Creative AI",
            "Strategic Advisor"
        ]
    )
    
    persona_instructions = {
        "Coding Expert": "You are an expert software engineer. Provide clean, optimized code with short explanations.",
        "Business Consultant": "You are an experienced business consultant. Give strategic, professional, and market-oriented advice.",
        "Creative AI": "You are a creative writer and storyteller. Think outside the box and use poetic or engaging language.",
        "Strategic Advisor": "You are a tactical advisor. Analyze scenarios critically and offer structured, step-by-step solutions."
    }

    if st.button("Clear Memory"):
        st.session_state.messages = []
        st.rerun()

# ================= TITLE =================

st.markdown("""
<div class="main-title">
🤖 AI ChatBot (GEMINI POWERED)
</div>

<div class="subtitle">
Next-generation AI assistant powered by Google Gemini
</div>
""", unsafe_allow_html=True)

# ================= CHAT LOGIC =================

if "messages" not in st.session_state:
    st.session_state.messages = []

# Purani history screen par dikhane ke liye
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
prompt = st.chat_input("Ask anything...")

if prompt:
    # User message show karein aur save karein
    with st.chat_message("user"):
        st.markdown(prompt)
        
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Bot response section (Live Streaming Output)
    with st.chat_message("assistant"):
        
        # History ko naye SDK ke Content/Part format mein convert karna
        formatted_history = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            formatted_history.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=m["content"])]
                )
            )

        current_instruction = persona_instructions[persona]
        
        try:
            # st.write_stream generator se real-time chunks lekar live print karega
            answer = st.write_stream(
                chat_with_gemini_stream(prompt, formatted_history, current_instruction)
            )
            
            # Streaming mukammal hone ke baad poora answer state mein save karein
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })
        except Exception as e:
            st.error(f"Error occurred: {e}")