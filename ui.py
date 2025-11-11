import streamlit as st
from streamlit_option_menu import option_menu
import requests
import json

# --- Configuration ---
FLASK_BACKEND_URL = "http://127.0.0.1:5001"
st.set_page_config(page_title="Profile Fusion", layout="wide")


# --- Session State Initialization ---
def init_session_state():
    defaults = {
        'is_logged_in': False,
        'user_info': None,
        'profile_id': None,
        'enhanced_profile': None,
        'api_session': requests.Session()  # Persist cookies across requests
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# --- API Helper Functions ---
def api_register(username, email, password):
    payload = {"username": username, "email": email, "password": password}
    return requests.post(f"{FLASK_BACKEND_URL}/api/register", json=payload)


def api_login(email, password):
    payload = {"email": email, "password": password}
    response = st.session_state.api_session.post(f"{FLASK_BACKEND_URL}/api/login", json=payload)
    if response.status_code == 200:
        st.session_state.is_logged_in = True
        st.session_state.user_info = response.json().get("user")
        st.rerun()  # CORRECTED
    else:
        st.error(response.json().get("error", "Login failed."))


def api_logout():
    st.session_state.api_session.post(f"{FLASK_BACKEND_URL}/api/logout")
    # Clear all session data on logout
    st.session_state.clear()
    init_session_state()  # Re-initialize with defaults
    st.rerun()  # CORRECTED


def api_create_profile():
    response = st.session_state.api_session.post(f"{FLASK_BACKEND_URL}/api/profiles")
    if response.status_code == 201:
        st.session_state.profile_id = response.json().get("profile_id")
        return True
    st.error(f"Failed to create profile: {response.json().get('error')}")
    return False


def api_add_source(profile_id, source_type, url=None, file=None):
    endpoint = f"{FLASK_BACKEND_URL}/api/profiles/{profile_id}/add_source"

    data = {'source_type': source_type}
    files = None

    if source_type == 'cv' and file:
        files = {'file': (file.name, file.getvalue(), file.type)}
    elif url:
        data['url'] = url
    else:
        return None, "Missing URL or File"

    with st.spinner(f"Processing {source_type}... This may take a moment."):
        response = st.session_state.api_session.post(endpoint, data=data, files=files)

    if response.status_code == 200:
        return response.json(), None
    else:
        try:
            error_message = response.json().get("error", "An unknown error occurred.")
        except requests.exceptions.JSONDecodeError:
            error_message = f"An unexpected server error occurred (Status: {response.status_code})."
        return None, error_message


# --- UI Rendering Functions ---
def render_auth_page():
    st.title("Welcome to Profile Fusion ✨")
    st.markdown("Unify your professional identity from across the web.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.form_submit_button("Login"):
                if email and password:
                    api_login(email, password)
                else:
                    st.warning("Please enter both email and password.")

    with col2:
        st.subheader("Register")
        with st.form("register_form"):
            username = st.text_input("Username", key="reg_user")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pass")
            if st.form_submit_button("Register"):
                if username and email and password:
                    response = api_register(username, email, password)
                    if response.status_code == 201:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(response.json().get("error", "Registration failed."))
                else:
                    st.warning("Please fill all fields.")


def render_dashboard():
    st.sidebar.title(f"Welcome, {st.session_state.user_info['username']}!")
    st.sidebar.button("Logout", on_click=api_logout)
    st.sidebar.info(f"Active Profile ID: \n`{st.session_state.profile_id}`")

    st.title("Profile Management Dashboard")
    st.markdown("Add sources to build and enhance your unified profile.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("➕ Add Data Sources")

        with st.expander("Upload CV (.pdf, .docx)", expanded=True):
            with st.form("cv_form", clear_on_submit=True):
                uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx'])
                if st.form_submit_button("Process CV"):
                    if uploaded_file:
                        json_response, error = api_add_source(st.session_state.profile_id, 'cv', file=uploaded_file)
                        if error:
                            st.error(f"CV Processing Failed: {error}")
                        else:
                            st.success("CV processed successfully!")
                            st.session_state.enhanced_profile = json_response.get("enhanced_profile")
                            st.rerun()  # CORRECTED

        with st.expander("Add LinkedIn Profile"):
            with st.form("linkedin_form", clear_on_submit=True):
                linkedin_url = st.text_input("LinkedIn Profile URL")
                if st.form_submit_button("Process LinkedIn"):
                    if linkedin_url:
                        json_response, error = api_add_source(st.session_state.profile_id, 'linkedin', url=linkedin_url)
                        if error:
                            st.error(f"LinkedIn Processing Failed: {error}")
                        else:
                            st.success("LinkedIn profile processed successfully!")
                            st.session_state.enhanced_profile = json_response.get("enhanced_profile")
                            st.rerun()  # CORRECTED

        with st.expander("Add GitHub Profile"):
            with st.form("github_form", clear_on_submit=True):
                github_url = st.text_input("GitHub Profile URL")
                if st.form_submit_button("Process GitHub"):
                    if github_url:
                        json_response, error = api_add_source(st.session_state.profile_id, 'github', url=github_url)
                        if error:
                            st.error(f"GitHub Processing Failed: {error}")
                        else:
                            st.success("GitHub profile processed successfully!")
                            st.session_state.enhanced_profile = json_response.get("enhanced_profile")
                            st.rerun()  # CORRECTED

    with col2:
        st.subheader("📄 Enhanced Profile")
        if st.session_state.enhanced_profile:
            profile = st.session_state.enhanced_profile
            st.text_input("Name", profile.get("name", ""), disabled=True)
            st.text_area("AI Enhanced Summary", profile.get("summary", "Not available."), height=150, disabled=True)

            if profile.get("skills"):
                st.write("**Skills:**")
                # Use a more visually appealing way to show skills
                st.markdown(
                    " ".join(f"`{skill}`" for skill in profile["skills"]),
                    unsafe_allow_html=True
                )

            # Display other details in an expandable JSON view
            with st.expander("View Full Profile Data"):
                st.json(profile)
        else:
            st.info("Your enhanced profile will be displayed here after you add a data source.")


# --- Main App Logic ---
init_session_state()

if not st.session_state.is_logged_in:
    render_auth_page()
else:
    # On first login, ensure a profile exists
    if not st.session_state.profile_id:
        with st.spinner("Setting up your workspace..."):
            if not api_create_profile():
                st.error("Fatal error: Could not create a user profile. Please try logging in again.")
                st.stop()
        st.rerun()  # CORRECTED: Rerun to load dashboard with profile_id

    render_dashboard()