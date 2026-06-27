import streamlit as st
import jwt
import datetime
import os
import visoes.home as page_home
import visoes.mapa as page_mapa
import visoes.financeiro as page_financeiro

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Barba System - Login",
    page_icon="💈",
    layout="wide"
)

# --- SECURITY SETTINGS (MOCK) ---
# Using environment variables with a fallback for demonstration purposes
SECRET_KEY = os.getenv("JWT_SECRET", "mock_secret_key_barba_123")

# Mock database for portfolio demonstration
MOCK_USERS = {
    "admin": {"password": "123", "role": "TOTAL", "branch": "ALL", "name": "Boss"},
    "south": {"password": "123", "role": "RESTRICTED", "branch": "SOUTH_ZONE", "name": "Ronaldo Fenômeno"},
    "north": {"password": "123", "role": "RESTRICTED", "branch": "NORTH_ZONE", "name": "René Higuita"},
    "down":  {"password": "123", "role": "RESTRICTED", "branch": "DOWNTOWN", "name": "Roberto Baggio"},
    "west":  {"password": "123", "role": "RESTRICTED", "branch": "WEST_ZONE", "name": "Dennis Rodman"},
    "baixada": {"password": "123", "role": "RESTRICTED", "branch": "BAIXADA_ZONE", "name": "Giorno Giovanna"}
}

# --- AUTHENTICATION FUNCTIONS ---
def generate_jwt_token(user_info):
    """Generates a JWT token with an expiration time to simulate enterprise auth."""
    payload = {
        "name": user_info["name"],
        "role": user_info["role"],
        "branch": user_info["branch"],
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def process_login(username, password):
    """Validates credentials and saves the token in the session state."""
    if username in MOCK_USERS and MOCK_USERS[username]["password"] == password:
        info = MOCK_USERS[username]
        token = generate_jwt_token(info)
        
        # Save token and user info in Streamlit's session state
        st.session_state["jwt_token"] = token
        st.session_state["logged_user"] = info
        return True
    return False

def logout():
    """Clears the session state to log the user out."""
    st.session_state.clear()

# --- LOGIN INTERFACE ---
def login_screen():
    st.markdown("<h1 style='text-align: center;'>💈 Barba System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Barbershop Management Hub</p>", unsafe_allow_html=True)
    
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            user_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            submit = st.form_submit_button("Log In", use_container_width=True)
            
            if submit:
                if process_login(user_input, password_input):
                    st.success("Login successful!")
                    st.rerun() # Reloads the app to apply the logged state
                else:
                    st.error("Invalid username or password.")
                    
        st.markdown("""
        <div style='text-align: center; font-size: 0.8em; color: gray; margin-top: 20px;'>
            <b>Test Credentials:</b><br>
            Admin: <code>admin / 123</code><br>
            South Zone: <code>south / 123</code> | North Zone: <code>north / 123</code><br>
            Downtown: <code>down / 123</code> | West Zone: <code>west / 123</code><br>
            Baixada: <code>baixada / 123</code>
        </div>
    """, unsafe_allow_html=True)

# --- APP ROUTER (THE GATEKEEPER) ---
# Check if the user is authenticated
if "jwt_token" not in st.session_state:
    login_screen()
else:
    # --- LOGGED IN AREA ---
    user = st.session_state["logged_user"]
    
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown(f"### Hello, {user['name']} 👋")
        st.markdown(f"**Role:** {user['role']}")
        st.markdown(f"**Branch:** {user['branch']}")
        st.divider()
        
        # --- NAVIGATION MENU ---
        menu = st.radio(
            "📍 Main Menu",
            ["Executive Dashboard", "Financial Details", "Geospatial Map"]
        )
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

    # --- ROUTING BASED ON THE SELECTED MENU ---
    if user["role"] in ["TOTAL", "RESTRICTED"]:
        if menu == "Executive Dashboard":
            page_home.renderizar()
        elif menu == "Financial Details":
            st.title("💸 Financial Details")
            page_financeiro.renderizar()
        elif menu == "Geospatial Map":
            page_mapa.renderizar()