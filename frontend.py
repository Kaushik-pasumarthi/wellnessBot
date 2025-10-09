import streamlit as st
import requests
from datetime import datetime
import uuid
st.set_page_config(page_title="Wellness AI Assistant", layout="wide", initial_sidebar_state="collapsed")

# Import DialogueManager
try:
    from dialogue_manager import DialogueManager
    DIALOGUE_MANAGER_AVAILABLE = True
except ImportError:
    DIALOGUE_MANAGER_AVAILABLE = False
    st.warning("DialogueManager not available. Chatbot functionality will be limited.")

# --- Configuration ---
BASE_URL = "http://127.0.0.1:5000"

# --- Modern ChatGPT-like Styles ---
st.markdown(
    """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root Variables */
    :root {
        --primary: #10a37f;
        --primary-dark: #0d8f72;
        --secondary: #f7f7f8;
        --accent: #6366f1;
        --text-primary: #0d1117;
        --text-secondary: #656d76;
        --background: #ffffff;
        --surface: #f8f9fa;
        --border: #e1e5e9;
        --shadow: 0 2px 8px rgba(0,0,0,0.1);
        --radius: 12px;
    }
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* Modern Card Styling */
    .main-card {
        background: var(--background) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow) !important;
        padding: 2rem !important;
        margin: 1rem 0 !important;
        border: 1px solid var(--border) !important;
    }
    
    /* Typography */
    .icon-green {
        color: var(--primary) !important;
        font-weight: 700 !important;
        text-shadow: none !important;
    }
    
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
    }
    
    /* Input Styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        background: var(--background) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-secondary) !important;
        opacity: 1 !important;
    }
    
    /* Button Styling */
    .stButton > button {
        border-radius: var(--radius) !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        border: none !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !im   portant;
        font-size: 14px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--secondary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
    </style>
""", unsafe_allow_html=True)

BASE_URL = "http://127.0.0.1:5000"  

def submit_review(bot_response, review_type, comment):
    """Submit review for bot response"""
    try:
        review_data = {
            "user_email": st.session_state.get("email", "anonymous@example.com"),
            "bot_response": bot_response,
            "review_type": review_type
        }
        
        if comment:
            review_data["comment"] = comment
            
        response = requests.post(f"{BASE_URL}/review", json=review_data)
        
        if response.status_code == 200:
            return True
        else:
            st.error("Failed to submit review")
            return False
            
    except Exception as e:
        st.error(f"Error submitting review: {str(e)}")
        return False

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if "email" not in st.session_state:
    st.session_state.email = ""
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Chat-related session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "dialogue_manager" not in st.session_state and DIALOGUE_MANAGER_AVAILABLE:
    st.session_state.dialogue_manager = DialogueManager()



def login_page():
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="main-card">
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 class="icon-green">Hey, Welcome Back !!</h1>
                <p style="color: var(--text-secondary); margin-top: 0.5rem;">Sign in to your wellness account</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        login_clicked = st.button("Sign In", key="login", help="Login", use_container_width=True)
        signup_clicked = st.button("Create Account", key="signup", help="Create Account", use_container_width=True)
        
        # Admin login section
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
        st.markdown("### 🔐 Admin Access")
        admin_login_clicked = st.button("Admin Dashboard", key="admin_dashboard", help="Access Admin Dashboard", use_container_width=True)
        forgot_clicked = st.button("Forgot Password?", key="forgot", use_container_width=True)

        st.markdown("""
            <style>
                div[data-testid="stButton"][key="login"] button {
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
                    color: white !important;
                    border: none !important;
                }
                div[data-testid="stButton"][key="signup"] button {
                    background: var(--surface) !important;
                    color: var(--text-primary) !important;
                    border: 2px solid var(--border) !important;
                }
                div[data-testid="stButton"][key="admin_dashboard"] button {
                    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
                    color: white !important;
                    border: none !important;
                    font-weight: bold !important;
                }
                div[data-testid="stButton"][key="forgot"] button {
                    background: transparent !important;
                    color: var(--primary) !important;
                    border: 2px solid var(--primary) !important;
                }
            </style>
        """, unsafe_allow_html=True)

    if login_clicked:
        response = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})
        data = response.json()
        if data["success"]:
            st.session_state.authenticated = True
            st.session_state.page = "profile"
            st.session_state.email = email
            # Reset chat-related session state for new user
            st.session_state.chat_history = []
            st.session_state.conversations_loaded = False
            st.success(data["message"])
            st.rerun()
        else:
            st.error(data["message"])

    if signup_clicked:
        st.session_state.page = "create_account"
        st.rerun()

    if admin_login_clicked:
        # Redirect to admin dashboard
        st.info("🔐 Opening Admin Dashboard...")
        st.markdown("""
        <script>
        window.open('http://localhost:8502', '_blank');
        </script>
        """, unsafe_allow_html=True)
        st.markdown("**Admin Dashboard:** http://localhost:8502")
        st.markdown("**Default Login:** Username: `admin`, Password: `admin123`")

    if forgot_clicked:
        st.session_state.page = "reset_password"
        st.rerun()


def create_account_page():
    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="main-card">
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 class="icon-green">🆕 Create Account</h1>
                <p style="color: var(--text-secondary); margin-top: 0.5rem;">Join the wellness community</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Create a strong password")

        signup_clicked = st.button("Create Account", key="signup_create", use_container_width=True)
        back_clicked = st.button("Back to Login", key="back_login", use_container_width=True)

        st.markdown("""
            <style>
                div[data-testid="stButton"][key="signup_create"] button {
                    background: linear-gradient(135deg, var(--accent) 0%, #5a67d8 100%) !important;
                    color: white !important;
                    border: none !important;
                }
                div[data-testid="stButton"][key="back_login"] button {
                    background: var(--surface) !important;
                    color: var(--text-primary) !important;
                    border: 2px solid var(--border) !important;
                }
            </style>
        """, unsafe_allow_html=True)

    if signup_clicked:
        response = requests.post(f"{BASE_URL}/signup", json={"email": email, "password": password})
        st.write("DEBUG response:", response.text)
        try:
            data = response.json()
            if response.status_code == 200 and data.get("success"):
                st.success(data.get("message", "Account created successfully"))
                st.session_state.email = email
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Signup failed: " + data.get("message", response.text))
        except requests.exceptions.JSONDecodeError:
            st.error("Signup failed: Invalid response from server.")

    if back_clicked:
        st.session_state.page = "login"
        st.rerun()

def reset_password_page():
    st.title("🔑 Reset Password")
    email = st.text_input("Email")
    old_password = st.text_input("Old Password", type="password")
    new_password = st.text_input("New Password", type="password")

    if st.button("Update Password"):
        res = requests.post(f"{BASE_URL}/reset_password", json={
            "email": email,
            "old_password": old_password,
            "new_password": new_password
        })

        if res.json().get("success"):
            st.success("✅ Password updated successfully!")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("❌ " + res.json().get("message"))

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


def profile_page():
    # Modern Profile Header
    st.markdown(
    """
    <style>
    /* Make Streamlit text inputs blend into card */
    div[data-baseweb="input"] {
        background-color: transparent !important;
        box-shadow: none !important;
        border: 1px solid #ccc !important;
        border-radius: 10px !important;
        padding: 8px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
    )

# Now one card containing everything
    st.markdown(
    """
    <div class="main-card" style="padding: 2rem; text-align: center; margin-bottom: 2rem;">
        <h1 class="icon-green">👤 Your Profile</h1>
        <p style="color: var(--text-secondary); margin-top: 0.5rem;">Manage your wellness account</p>
    """,
    unsafe_allow_html=True
    )
    
    email = st.session_state.get("email")
    response = requests.get(f"{BASE_URL}/profile", params={"email": email})
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        st.error("Failed to load profile: Invalid response from server.")
        return

    if not data["success"]:
        st.error("Not logged in.")
        st.session_state.authenticated = False
        st.session_state.page = "login"
        st.rerun()

    profile = data["profile"]

    # Profile form in a modern card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        
        name = st.text_input("Full Name", profile["name"], placeholder="Enter your full name")
        age_group = st.selectbox(
            "Age Group",
            ["<18", "18-25", "26-35", "36-50", "50+"],
            index=["<18", "18-25", "26-35", "36-50", "50+"].index(profile["age_group"] or "18-25")
        )
        language = st.selectbox(
            "Preferred Language",
            ["English", "Telugu", "Hindi"],
            index=["English", "Telugu", "Hindi"].index(profile["language"] or "English")
        )

        st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons in a modern layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        update_clicked = st.button("💾 Update Profile", key="update_profile", use_container_width=True)
    with col2:
        chatbot_clicked = st.button("🤖 Start Wellness Chat", key="start_chat", use_container_width=True)
    with col3:
        feedback_clicked = st.button("📝 Feedback", key="feedback", use_container_width=True)
    with col4:
        logout_clicked = st.button("🚪 Logout", key="logout", use_container_width=True)

    st.markdown("""
        <style>
            div[data-testid="stButton"][key="update_profile"] button {
                background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
                color: white !important;
                border: none !important;
            }
            div[data-testid="stButton"][key="start_chat"] button {
                background: linear-gradient(135deg, var(--accent) 0%, #5a67d8 100%) !important;
                color: white !important;
                border: none !important;
            }
            div[data-testid="stButton"][key="feedback"] button {
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
                color: white !important;
                border: none !important;
            }
            div[data-testid="stButton"][key="logout"] button {
                background: var(--surface) !important;
                color: var(--text-primary) !important;
                border: 2px solid var(--border) !important;
            }
        </style>
    """, unsafe_allow_html=True)

    if update_clicked:
        response = requests.post(f"{BASE_URL}/profile", json={"email": email, "name": name, "age_group": age_group, "language": language})
        st.success(response.json()["message"])

    if chatbot_clicked:
        st.session_state.page = "chatbot"
        st.rerun()

    if feedback_clicked:
        st.session_state.page = "feedback"
        st.rerun()

    if logout_clicked:
        st.session_state.authenticated = False
        st.session_state.page = "login"
        # Clear chat-related session state on logout
        st.session_state.chat_history = []
        st.session_state.conversations_loaded = False
        st.session_state.email = ""
        st.rerun()


def chatbot_page():
    """Modern ChatGPT-like Wellness Bot Interface"""
    
    # Modern Header
    st.markdown("""
    <div style="background: var(--background); border-radius: var(--radius); 
                box-shadow: var(--shadow); padding: 1.5rem; margin-bottom: 2rem;
                border: 1px solid var(--border);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; color: var(--primary); font-size: 1.8rem;">
                    🤖 Wellness AI Assistant
                </h1>
                <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 0.9rem;">
                    Your personal health companion powered by AI
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1.5])
    
    with col1:
        if st.button("← Back to Profile", key="back_to_profile", use_container_width=True):
            st.session_state.page = "profile"
            st.rerun()
    
    with col2:
        # Language toggle button
        if "chat_language" not in st.session_state:
            st.session_state.chat_language = "english"
        
        current_lang = st.session_state.chat_language
        button_text = "🇮🇳 हिन्दी" if current_lang == "english" else "🇺🇸 English"
        
        if st.button(button_text, key="language_toggle", use_container_width=True):
            st.session_state.chat_language = "hindi" if current_lang == "english" else "english"
            
            # Update language in wellness bot
            if DIALOGUE_MANAGER_AVAILABLE:
                st.session_state.dialogue_manager.wellness_bot.set_language(
                    st.session_state.session_id, 
                    st.session_state.chat_language
                )
                
                # If the only message is a greeting, refresh it with new language
                if (len(st.session_state.chat_history) == 1 and 
                    st.session_state.chat_history[0].get("user") is None):
                    new_greeting = st.session_state.dialogue_manager.get_greeting(st.session_state.session_id)
                    st.session_state.chat_history[0]["bot"] = new_greeting
                else:
                    # Add language change message for existing conversations
                    lang_change_msg = "भाषा हिन्दी में बदल गई है। अब आप हिन्दी में अपने स्वास्थ्य संबंधी प्रश्न पूछ सकते हैं।" if st.session_state.chat_language == "hindi" else "Language changed to English. You can now ask your health questions in English."
                    
                    st.session_state.chat_history.append({
                        "user": None,
                        "bot": lang_change_msg,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
            
            st.rerun()
    
    with col4:
        if st.button("🗑 Clear Chat", key="clear_chat", use_container_width=True):
            # Clear local chat history
            st.session_state.chat_history = []
            
            # Clear conversations from database if dialogue manager is available
            if DIALOGUE_MANAGER_AVAILABLE and st.session_state.get("email"):
                success = st.session_state.dialogue_manager.clear_user_conversations(st.session_state.email)
                if success:
                    st.success("Chat history cleared!")
                else:
                    st.warning("Local chat cleared, but couldn't clear database history.")
            
            st.rerun()

    # Load previous conversations on first visit
    if "conversations_loaded" not in st.session_state:
        st.session_state.conversations_loaded = True
        
        if DIALOGUE_MANAGER_AVAILABLE and st.session_state.get("email"):
            # Load previous conversations from database
            previous_conversations = st.session_state.dialogue_manager.get_user_conversations(
                st.session_state.email, limit=20
            )
            
            if previous_conversations:
                st.session_state.chat_history = []
                for conv in previous_conversations:
                    # Parse timestamp to get just time part
                    timestamp = conv.get("timestamp", "")
                    if timestamp:
                        try:
                            dt = datetime.strptime(timestamp.split()[0] + " " + timestamp.split()[1], "%Y-%m-%d %H:%M:%S")
                            formatted_time = dt.strftime("%H:%M")
                        except:
                            formatted_time = timestamp
                    else:
                        formatted_time = ""
                    
                    st.session_state.chat_history.append({
                        "user": conv.get("user"),
                        "bot": conv.get("bot"),
                        "timestamp": formatted_time
                    })
                
                st.info(f"📚 Loaded {len(previous_conversations)} previous conversations")

    # Initialize chat with greeting if empty and no previous conversations
    if not st.session_state.chat_history and DIALOGUE_MANAGER_AVAILABLE:
        # Set language before getting greeting
        current_language = st.session_state.get("chat_language", "english")
        st.session_state.dialogue_manager.wellness_bot.set_language(
            st.session_state.session_id, 
            current_language
        )
        greeting = st.session_state.dialogue_manager.get_greeting(st.session_state.session_id)
        st.session_state.chat_history.append({
            "user": None,  # None indicates this is a bot-initiated message
            "bot": greeting,
            "timestamp": datetime.now().strftime("%H:%M")
        })

    # Chat Display Container - ChatGPT Style
 
    if st.session_state.chat_history:
        for i, chat in enumerate(st.session_state.chat_history):
            timestamp = chat.get("timestamp", "")
            
            # Display user message - ChatGPT style
            if chat.get("user"):
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin: 1.5rem 0;">
                    <div style="
                        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
                        color: white;
                        padding: 12px 18px;
                        border-radius: 18px 18px 6px 18px;
                        max-width: 75%;
                        font-size: 14px;
                        line-height: 1.5;
                        box-shadow: 0 2px 8px rgba(16, 163, 127, 0.2);
                        word-wrap: break-word;
                    ">
                        <div style="font-weight: 600; margin-bottom: 4px; font-size: 12px; opacity: 0.9;">
                            You • {timestamp}
                        </div>
                        {chat["user"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Display bot message - ChatGPT style
            if chat.get("bot"):
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin: 1.5rem 0;">
                    <div style="
                        background: var(--surface);
                        color: var(--text-primary);
                        padding: 12px 18px;
                        border-radius: 18px 18px 18px 6px;
                        max-width: 75%;
                        font-size: 14px;
                        line-height: 1.5;
                        border: 1px solid var(--border);
                        word-wrap: break-word;
                    ">
                        <div style="font-weight: 600; margin-bottom: 4px; font-size: 12px; color: var(--primary);">
                            🤖 Wellness AI • {timestamp}
                        </div>
                        {chat["bot"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add review buttons after each bot response
                review_key_base = f"review_{len(st.session_state.chat_history)}_{i}"
                
                col1, col2, col3 = st.columns([1, 1, 8])
                
                with col1:
                    if st.button("👍", key=f"{review_key_base}_positive", help="Helpful response"):
                        submit_review(chat["bot"], "positive", None)
                        st.success("Thank you for your positive feedback!")
                
                with col2:
                    if st.button("👎", key=f"{review_key_base}_negative", help="Not helpful"):
                        # Show comment input for negative feedback
                        st.session_state[f"show_comment_{review_key_base}"] = True
                
                # Show comment input if negative review was clicked
                if st.session_state.get(f"show_comment_{review_key_base}", False):
                    comment = st.text_input(
                        "What could be improved?", 
                        key=f"{review_key_base}_comment",
                        placeholder="Please share how we can improve..."
                    )
                    
                    col_submit, col_cancel = st.columns(2)
                    
                    with col_submit:
                        if st.button("Submit", key=f"{review_key_base}_submit"):
                            submit_review(chat["bot"], "negative", comment)
                            st.session_state[f"show_comment_{review_key_base}"] = False
                            st.success("Thank you for your feedback!")
                            st.rerun()
                    
                    with col_cancel:
                        if st.button("Cancel", key=f"{review_key_base}_cancel"):
                            st.session_state[f"show_comment_{review_key_base}"] = False
                            st.rerun()
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0; color: var(--text-secondary);">
            <div style="font-size: 2rem; margin-bottom: 1rem;">💬</div>
            <h3 style="color: var(--text-primary); margin-bottom: 0.5rem;">Welcome to Wellness AI</h3>
            <p>Start a conversation about your health and wellness concerns</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Modern Input Area - ChatGPT Style
    st.markdown("""
    <div style="
        background: var(--background);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
    ">
    """, unsafe_allow_html=True)
    
    # Create form for input
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_area(
                "",
                key="user_message",
                placeholder="Message Wellness AI... (Type your symptoms, health questions, or concerns)",
                height=80,  # Must be >= 68
                label_visibility="collapsed"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing if needed
            send_clicked = st.form_submit_button("Send", use_container_width=True)

        # Help and example prompts
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.form_submit_button("❓ Help", use_container_width=True):
                if DIALOGUE_MANAGER_AVAILABLE:
                    # Set language before getting help
                    current_language = st.session_state.get("chat_language", "english")
                    st.session_state.dialogue_manager.wellness_bot.set_language(
                        st.session_state.session_id, 
                        current_language
                    )
                    help_message = st.session_state.dialogue_manager.get_help_message()
                    st.session_state.chat_history.append({
                        "user": "Help",
                        "bot": help_message,
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()
        
        with col2:
            if st.form_submit_button("💡 Examples", use_container_width=True):
                examples = """Here are some example questions you can ask:
                
• "I have a headache and feel tired"
• "What can I do for better sleep?"
• "I'm feeling anxious lately"
• "How can I boost my immune system?"
• "I have stomach pain after eating"
• "What are some stress management tips?"
                """
                st.session_state.chat_history.append({
                    "user": "Show examples",
                    "bot": examples,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Handle message sending
    if send_clicked and user_input.strip():
        if DIALOGUE_MANAGER_AVAILABLE:
            # Get bot response
            try:
                # Set language in dialogue manager before processing
                if hasattr(st.session_state.dialogue_manager, 'wellness_bot'):
                    current_language = st.session_state.get("chat_language", "english")
                    st.session_state.dialogue_manager.wellness_bot.set_language(
                        st.session_state.session_id, 
                        current_language
                    )
                
                bot_response = st.session_state.dialogue_manager.handle_input(
                    user_input, 
                    st.session_state.session_id,
                    st.session_state.get("email")  # Pass username for saving
                )
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "user": user_input,
                    "bot": bot_response,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.error("Chatbot functionality is not available. Please check if wellness_bot is properly installed.")

    # Statistics and info
    if st.session_state.chat_history:
        total_messages = len([chat for chat in st.session_state.chat_history if chat.get("user")])
        st.markdown(f"""
        <div style="text-align: center; margin-top: 2rem; color: var(--text-secondary); font-size: 0.85rem;">
            💬 {total_messages} messages in this conversation
        </div>
        """, unsafe_allow_html=True)

    # Enhanced CSS for chat styling
    st.markdown("""
        <style>
            /* Button Styling for Chat Page */
            div[data-testid="stButton"][key="back_to_profile"] button {
                background: var(--surface) !important;
                color: var(--text-primary) !important;
                border: 2px solid var(--border) !important;
            }
            
            div[data-testid="stButton"][key="clear_chat"] button {
                background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
                color: white !important;
                border: none !important;
            }
            
            div[data-testid="stButton"][key="language_toggle"] button {
                background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%) !important;
                color: white !important;
                border: none !important;
                font-weight: 600 !important;
            }
            
            /* Form styling */
            .stForm {
                border: none !important;
                padding: 0 !important;
                background: transparent !important;
            }
            
            /* Text area styling */
            .stTextArea > div > div > textarea {
                border: 2px solid var(--border) !important;
                border-radius: 12px !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 14px !important;
                resize: none !important;
            }
            
            .stTextArea > div > div > textarea:focus {
                border-color: var(--primary) !important;
                box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.1) !important;
            }
            
            /* Smooth scrolling for chat */
            #chat-container {
                scroll-behavior: smooth;
            }
            
            /* Animation for messages */
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* Loading animation */
            .typing-indicator {
                animation: pulse 1.5s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 0.6; }
                50% { opacity: 1; }
                100% { opacity: 0.6; }
            }
        </style>
    """, unsafe_allow_html=True)

def feedback_page():
    """Feedback page"""
    st.title("📝 Feedback & Support")
    
    st.markdown("""
    <div class="card">
        <h3>We value your feedback!</h3>
        <p>Help us improve the wellness bot by sharing your experience.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("feedback_form"):
        name = st.text_input("Name", placeholder="Enter your name")
        email = st.text_input("Email", placeholder="Enter your email")
        
        rating = st.select_slider(
            "Rating",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda x: "⭐" * x
        )
        
        feedback = st.text_area(
            "Feedback",
            placeholder="Share your thoughts, suggestions, or report issues...",
            height=150
        )
        
        submitted = st.form_submit_button("Submit Feedback", use_container_width=True)
        
        if submitted:
            if name and email and feedback:
                try:
                    response = requests.post(
                        "http://localhost:5000/feedback",
                        json={
                            "name": name,
                            "email": email,
                            "feedback": feedback,
                            "rating": rating
                        }
                    )
                    
                    if response.json().get("success"):
                        st.success("Thank you for your feedback! We appreciate your input.")
                        st.balloons()
                    else:
                        st.error("Failed to submit feedback. Please try again.")
                        
                except Exception as e:
                    st.error(f"Error submitting feedback: {str(e)}")
            else:
                st.error("Please fill in all required fields.")
    
    # Back to Profile button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Profile", key="back_to_profile_from_feedback", use_container_width=True):
        st.session_state.page = "profile"
        st.rerun()
    
    st.markdown("""
        <style>
            div[data-testid="stButton"][key="back_to_profile_from_feedback"] button {
                background: var(--surface) !important;
                color: var(--text-primary) !important;
                border: 2px solid var(--border) !important;
            }
        </style>
    """, unsafe_allow_html=True)

if not st.session_state.authenticated:
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "create_account":
        create_account_page()
    elif st.session_state.page == "reset_password":
        reset_password_page()
else:
    if st.session_state.page == "profile":
        profile_page()
    elif st.session_state.page == "chatbot":
        chatbot_page()
    elif st.session_state.page == "feedback":
        feedback_page()
    else:
        # Default to profile if unknown page
        st.session_state.page = "profile"
        profile_page()