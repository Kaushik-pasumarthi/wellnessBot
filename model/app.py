import streamlit as st
import time
import traceback
from dialogue_manager import RasaHealthBot

# Page config
st.set_page_config(
    page_title="Wellness Bot",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for better styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-container {
        background: rgba(255,255,255,0.1);
        padding: 2rem;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        margin: 1rem 0;
    }
    .header-title {
        text-align: center;
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .header-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 15px;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
        margin-bottom: 1rem;
        scroll-behavior: smooth;
    }
    .message {
        margin: 10px 0;
        animation: fadeIn 0.5s;
    }
    .user-message {
        display: flex;
        justify-content: flex-end;
    }
    .bot-message {
        display: flex;
        justify-content: flex-start;
    }
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 5px 18px;
        max-width: 70%;
        word-wrap: break-word;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }
    .bot-bubble {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 5px;
        max-width: 70%;
        word-wrap: break-word;
        box-shadow: 0 2px 10px rgba(17, 153, 142, 0.3);
    }
    .empty-state {
        text-align: center;
        color: rgba(255,255,255,0.7);
        font-style: italic;
        margin: 2rem 0;
    }
    .status-badge {
        background: #e8f5e8;
        color: #27ae60;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .help-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    .example-chat {
        background: #e8f4fd;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with error handling
def initialize_app():
    try:
        if 'initialized' not in st.session_state:
            st.session_state.chat_history = []
            st.session_state.session_id = f"user_{int(time.time())}"
            st.session_state.dialogue_manager = RasaHealthBot()
            st.session_state.dialogue_manager.start_session(st.session_state.session_id)
            st.session_state.initialized = True
            st.session_state.error_state = False
        return True
    except Exception as e:  
        st.session_state.error_state = True
        st.session_state.error_message = str(e)
        return False

# Initialize the app
app_ready = initialize_app()

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown('<h1 class="header-title">🏥 Wellness Bot</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Your AI-powered health and wellness assistant</p>', unsafe_allow_html=True)

if not app_ready or st.session_state.get('error_state', False):
    # Error state
    st.error("⚠️ There was an issue initializing the wellness bot.")
    st.code(st.session_state.get('error_message', 'Unknown error'))
    st.info("Please make sure all model files are available and try refreshing the page.")
else:
    # Controls row
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown('<div class="status-badge">🟢 Bot Ready</div>', unsafe_allow_html=True)
    
    with col2:
        if st.button("🗑️ Clear", key="clear_btn"):
            st.session_state.chat_history = []
            st.session_state.dialogue_manager.end_session(st.session_state.session_id)
            st.session_state.session_id = f"user_{int(time.time())}"
            st.session_state.dialogue_manager.start_session(st.session_state.session_id)
            st.rerun()
    
    with col3:
        msg_count = len(st.session_state.chat_history)
        st.write(f"💬 {msg_count} messages")

    # Chat display
    st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
    
    if st.session_state.chat_history:
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                st.markdown(f'''
                <div class="message user-message">
                    <div class="user-bubble">
                        👤 {message["content"]}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="message bot-message">
                    <div class="bot-bubble">
                        🤖 {message["content"]}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="empty-state">
            <h3>👋 Welcome!</h3>
            <p>Start a conversation by typing a message below.</p>
            <p>Ask me about symptoms, first aid, or wellness tips!</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # User input
    user_input = st.chat_input("💬 Ask me about your health concerns...")

    # Handle user input
    if user_input:
        try:
            # Add user message
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': time.time()
            })
            
            # Get bot response with progress
            with st.spinner("🤖 Analyzing your message..."):
                bot_response = st.session_state.dialogue_manager.handle(
                    user_input, 
                    st.session_state.session_id
                )
            
            # Add bot response
            st.session_state.chat_history.append({
                'role': 'bot',
                'content': bot_response,
                'timestamp': time.time()
            })
            
            # Auto-scroll to bottom
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error processing your message: {str(e)}")
            st.code(traceback.format_exc())

    # Help section
    with st.expander("❓ How to use this bot", expanded=False):
        st.markdown('''
        <div class="help-section">
            <h4>🎯 What can you ask?</h4>
            <ul>
                <li><strong>🤒 Symptoms:</strong> "I have a headache", "I feel dizzy", "I'm nauseous"</li>
                <li><strong>🩹 First Aid:</strong> "How to treat a cut?", "What to do for burns?"</li>
                <li><strong>💪 Wellness:</strong> "How to sleep better?", "Tips for staying healthy"</li>
                <li><strong>👋 General:</strong> Start with "Hi" or introduce yourself</li>
            </ul>
            
            <h4>💡 Example Conversation:</h4>
            <div class="example-chat">
You: Hi, my name is Alex<br>
Bot: Hello Alex! How are you feeling today?<br>
You: I have a severe headache since yesterday<br>
Bot: A severe headache since yesterday can be concerning, Alex. Are you experiencing any other symptoms?<br>
You: Yes, I feel nauseous too<br>
Bot: Thank you for the details, Alex. Severe headache with nausea that started yesterday could indicate several things...
            </div>
            
            <h4>🔬 Features:</h4>
            <ul>
                <li>✅ Remembers your name and conversation context</li>
                <li>✅ Asks follow-up questions for better understanding</li>
                <li>✅ Provides personalized responses</li>
                <li>✅ Extracts symptoms, severity, and timing</li>
                <li>✅ Suggests when to seek professional help</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

    # Session info (for debugging)
    if st.checkbox("🔧 Show session info (for debugging)"):
        if hasattr(st.session_state.dialogue_manager, 'sessions'):
            session_data = st.session_state.dialogue_manager.sessions.get(st.session_state.session_id, {})
            st.json({
                "session_id": st.session_state.session_id,
                "state": session_data.get('state'),
                "slots": session_data.get('slots', {}),
                "user_name": session_data.get('user_name'),
                "last_intent": session_data.get('last_intent'),
                "total_messages": len(st.session_state.chat_history)
            })

# Footer
st.markdown('''
<div style="text-align: center; margin-top: 2rem; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px;">
    <p style="color: white;"><strong>💡 Wellness Tip:</strong> This bot provides general wellness information and tips.</p>
    <p style="color: white;">Always consult healthcare professionals for medical advice.</p>
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
