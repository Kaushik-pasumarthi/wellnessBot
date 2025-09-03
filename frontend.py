import streamlit as st
import requests

# --- Configuration ---
BASE_URL = "http://127.0.0.1:5000"
st.set_page_config(page_title="Text Summarisation AI", layout="centered", initial_sidebar_state="collapsed")

# --- Styles ---
st.markdown(
    """
    <style>
      :root{
        --primary:#27ae60;
        --muted:#6c757d;
        --card:#ffffff;
        --accent:#bdc3c7;
      }
      .block-container{padding-top:1.5rem;}
            background-color: #bdc3c7 !important;
            color: #333 !important;
        }
        .icon-green {
            color: #27ae60 !important;
        }
        /* Fix input box visibility */
        input, textarea {
            background-color: #fff !important;
            color: #111 !important;
        }
        .stTextInput>div>div>input {
            background-color: #fff !important;
            color: #111 !important;
        }
      .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background:#fbfdff !important;
        color:#222 !important;           # <-- Make input text dark
        border:1px solid #e6eef9 !important;
        padding:10px 12px !important;
        border-radius:8px !important;
      }
      .stTextInput>div>div>input::placeholder {
        color: #94a3b8 !important;       # <-- Placeholder is lighter gray
        opacity: 1 !important;
      }
    </style>
""", unsafe_allow_html=True)

BASE_URL = "http://127.0.0.1:5000"  
st.set_page_config(page_title="Authenticator", layout="centered")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "login"



def login_page():
    st.markdown('<h1 class="icon-green">🔑 Login</h1>', unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    login_clicked = st.button("Login", key="login", help="Login", use_container_width=True)
    signup_clicked = st.button("Create Account", key="signup", help="Create Account", use_container_width=True)
    forgot_clicked = st.button("Forgot Password?", key="forgot", use_container_width=True)

    st.markdown("""
        <style>
            div[data-testid="stButton"][key="login"] button {background-color: #27ae60; color: #fff;}
            div[data-testid="stButton"][key="signup"] button {background-color: #bdc3c7; color: #333;}
            div[data-testid="stButton"][key="forgot"] button {background-color: #fff; color: #27ae60; border: 1px solid #27ae60;}
        </style>
    """, unsafe_allow_html=True)

    if login_clicked:
        response = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})
        data = response.json()
        if data["success"]:
            st.session_state.authenticated = True
            st.session_state.page = "profile"
            st.session_state.email = email
            st.success(data["message"])
            st.rerun()
        else:
            st.error(data["message"])

    if signup_clicked:
        st.session_state.page = "create_account"
        st.rerun()

    if forgot_clicked:
        st.session_state.page = "reset_password"
        st.rerun()


def create_account_page():
    st.markdown('<h1 class="icon-green">🆕 Create Account</h1>', unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    signup_clicked = st.button("Sign Up", key="signup_create", use_container_width=True)
    back_clicked = st.button("Back to Login", key="back_login", use_container_width=True)

    st.markdown("""
        <style>
            div[data-testid="stButton"][key="signup_create"] button {background-color: #bdc3c7; color: #333;}
            div[data-testid="stButton"][key="back_login"] button {background-color: #27ae60; color: #fff;}
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
    st.markdown('<h1 class="icon-green">👤 Profile</h1>', unsafe_allow_html=True)
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

    name = st.text_input("Name", profile["name"])
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

    update_clicked = st.button("Update Profile", key="update_profile", use_container_width=True)
    logout_clicked = st.button("Logout", key="logout", use_container_width=True)

    st.markdown("""
        <style>
            div[data-testid="stButton"][key="update_profile"] button {background-color: #27ae60; color: #fff;}
            div[data-testid="stButton"][key="logout"] button {background-color: #bdc3c7; color: #333;}
        </style>
    """, unsafe_allow_html=True)

    if update_clicked:
        response = requests.post(f"{BASE_URL}/profile", json={"email": email, "name": name, "age_group": age_group, "language": language})
        st.success(response.json()["message"])

    if logout_clicked:
        st.session_state.authenticated = False
        st.session_state.page = "login"
        st.rerun()

if not st.session_state.authenticated:
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "create_account":
        create_account_page()
    elif st.session_state.page == "reset_password":
        reset_password_page()
else:
    profile_page()