import os
import uuid
from flask import Flask, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename

# --- NEW Authentication and Security Imports ---
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt

# --- Database and Form Imports ---
from database.models import db, Profile, Skill, User
from forms import LoginForm, RegistrationForm

# --- Core Service Imports ---
from unification_service.unifier import ProfileUnifier
from enhancement_service.enhancer import ProfileEnhancer
# The embedding service is not used in this version, so it's not imported.

# --- Extractor Module Imports ---
from cv_extractor import extract_cv_data
from linkedin_extractor.scraper import collect_profile_from_linkedin_url
from github_extractor.api_client import get_profile_from_github_url

# ==============================================================================
# --- App Configuration & Initialization ---
# ==============================================================================

app = Flask(__name__)

# CRITICAL: Set a secret key for session management and form protection (CSRF).
# In a production environment, this MUST be a long, random string loaded from an
# environment variable to keep it secure.
app.config['SECRET_KEY'] = 'a-very-secret-and-random-key-for-this-poc'

# Configure the SQLite database. This will create a 'profiles.db' file.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///profiles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure the folder for temporary file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Initialize All Services and Extensions ---
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# If a user who is not logged in tries to access a protected page,
# they will be redirected to the 'login' page.
#login_manager.login_view = 'login'
#login_manager.login_message_category = 'info'  # For styling flashed messages

# Initialize our custom services
unifier = ProfileUnifier()
enhancer = ProfileEnhancer()


# --- KEY CHANGE #1: Custom Unauthorized Handler ---
# Instead of redirecting to a login page, we will return a JSON 401 Unauthorized error.
# This is what an API client (like Streamlit) expects.
@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Authentication required. Please log in."}), 401

# This callback function is required by Flask-Login.
# It's used to reload the user object from the user ID stored in the session.
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ==============================================================================
# --- API-Friendly Authentication Routes ---
# ==============================================================================

@app.route("/api/register", methods=['POST'])
def api_register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({"error": "Missing data"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 409  # 409 Conflict

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], email=data['email'], password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@app.route("/api/login", methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing data"}), 400

    user = User.query.filter_by(email=data.get('email')).first()
    if user and bcrypt.check_password_hash(user.password_hash, data.get('password')):
        login_user(user)  # This sets the session cookie
        return jsonify({
            "message": "Login successful",
            "user": {"username": user.username, "email": user.email}
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/logout", methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200


@app.route("/api/user", methods=['GET'])
@login_required
def get_current_user():
    return jsonify({"username": current_user.username, "email": current_user.email})


# ==============================================================================
# --- Protected Core API Endpoints ---
# These are the main endpoints for your application's functionality.
# ==============================================================================

@app.route('/api/profiles', methods=['POST'])
@login_required  # Ensures only logged-in users can create profiles.
def create_profile():
    """Creates a new, empty profile record linked to the current user."""
    profile_id = str(uuid.uuid4())
    new_profile = Profile(id=profile_id, unified_profile_json={}, user_id=current_user.id)
    db.session.add(new_profile)
    db.session.commit()
    return jsonify({"message": "Profile created successfully", "profile_id": profile_id}), 201


@app.route('/api/profiles/<string:profile_id>/add_source', methods=['POST'])
@login_required  # Ensures only logged-in users can add sources.
def add_source_to_profile(profile_id):
    """
    The main workflow endpoint. It adds data from a source (CV, LinkedIn, GitHub)
    to a user's profile, triggering the full Unify -> Enhance -> Store pipeline.
    """
    # CRITICAL SECURITY CHECK: Ensure the user can only modify their own profile.
    # first_or_404() will automatically return a 404 Not Found error if no profile matches.
    profile = Profile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()

    source_type = request.form.get('source_type')
    new_data = None

    # --- Step 1: EXTRACT ---
    try:
        if source_type == 'cv':
            if 'file' not in request.files:
                return jsonify({"error": "No file part for 'cv' source_type"}), 400
            file = request.files['file']
            if file.filename and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                new_data = extract_cv_data(filepath)
            else:
                return jsonify({"error": "Invalid or missing file for 'cv' source_type"}), 400

        elif source_type == 'linkedin':
            url = request.form.get('url')
            if not url: return jsonify({"error": "Missing 'url' for 'linkedin' source_type"}), 400
            new_data = collect_profile_from_linkedin_url(url)

        elif source_type == 'github':
            url = request.form.get('url')
            if not url: return jsonify({"error": "Missing 'url' for 'github' source_type"}), 400
            new_data = get_profile_from_github_url(url)

        else:
            return jsonify({"error": "Invalid source_type. Must be 'cv', 'linkedin', or 'github'"}), 400

    except Exception as e:
        return jsonify({"error": f"Extraction failed: {str(e)}"}), 500

    # --- Step 2: UNIFY ---
    # This combines the new data with any existing data for the profile.
    unified_profile = unifier.unify(profile_id, new_data)

    # --- Step 3: ENHANCE ---
    # The unified data is polished by the LLM for consistency and presentation.
    enhanced_profile = enhancer.enhance(unified_profile)

    # --- Step 4: STORE ---
    # The final, enhanced profile is saved back to the database.
    profile.unified_profile_json = enhanced_profile.model_dump()

    # Update the relational Skill table for potential structured queries in the future.
    # Clear existing skills and add the new, enhanced list.
    profile.skills.clear()
    profile.skills = [Skill(name=skill_name) for skill_name in enhanced_profile.skills]

    db.session.commit()

    return jsonify({
        "message": f"Source '{source_type}' added and profile enhanced successfully.",
        "profile_id": profile_id,
        "enhanced_profile": enhanced_profile.model_dump()
    }), 200


# ==============================================================================
# --- Main Execution Block ---
# ==============================================================================

# --- Main Execution Block ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)