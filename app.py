import os
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# --- Database and ORM Imports (Commented Out) ---
# DB: from database.models import db, Profile, Skill

# --- Core Service Imports ---
from unification_service.unifier import ProfileUnifier
from enhancement_service.enhancer import ProfileEnhancer
# EMBEDDING: from embedding_service import EmbeddingService # Embedding part removed

# --- Extractor Module Imports ---
from cv_extractor import extract_cv_data
from linkedin_extractor.scraper import collect_profile_from_linkedin_url
from github_extractor.api_client import get_profile_from_github_url

# ==============================================================================
# --- App Configuration & Initialization ---
# ==============================================================================

app = Flask(__name__)

# --- Database Configuration (Commented Out) ---
# DB: app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///profiles.db'
# DB: app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure File Uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Initialize Services ---
# We only initialize the services needed for the in-memory pipeline.
unifier = ProfileUnifier()
enhancer = ProfileEnhancer()


# DB: db.init_app(app)
# EMBEDDING: embedding_service = EmbeddingService() # Embedding part removed


# ==============================================================================
# --- Helper Functions ---
# ==============================================================================

def allowed_file(filename):
    """Checks if a file's extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==============================================================================
# --- API Endpoints ---
# ==============================================================================

# NOTE: The /profiles and /profiles/<id>/add_source endpoints are combined into one
#       stateless endpoint since there is no database to persist a profile between calls.

@app.route('/process', methods=['POST'])
def process_profile_source():
    """
    A single, stateless endpoint to perform the full Extract -> Unify -> Enhance pipeline.
    It takes a data source, processes it in memory, and returns the final enhanced profile.
    """
    source_type = request.form.get('source_type')
    if not source_type:
        return jsonify({"error": "Missing 'source_type' (must be 'cv', 'linkedin', or 'github')"}), 400

    new_data = None

    # --- Step 1: EXTRACT ---
    try:
        if source_type == 'cv':
            if 'file' not in request.files:
                return jsonify({"error": "No file part for 'cv' source_type"}), 400
            file = request.files['file']
            if file.filename and allowed_file(file.filename):
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
            return jsonify({"error": f"Invalid source_type: '{source_type}'"}), 400

    except Exception as e:
        return jsonify({"error": f"Extraction failed: {str(e)}"}), 500

    # --- Step 2: UNIFY ---
    # We generate a temporary profile_id for this transaction.
    profile_id = str(uuid.uuid4())
    unified_profile = unifier.unify(profile_id, new_data)

    # --- Step 3: ENHANCE ---
    print(f"Enhancing unified profile for temporary id {profile_id}...")
    enhanced_profile = enhancer.enhance(unified_profile)

    # --- Step 4: RETURN RESULT ---
    # The pipeline finishes here. The final JSON is returned directly to the client.

    # DB: The following block for database persistence is commented out.
    # ---
    # DB: profile.unified_profile_json = enhanced_profile.model_dump()
    # DB: profile.skills = [Skill(name=skill_name) for skill_name in enhanced_profile.skills]
    # DB: profile.qdrant_id = profile_id
    # DB: db.session.commit()
    # ---

    # EMBEDDING: The following line for embedding is removed.
    # ---
    # EMBEDDING: embedding_service.embed_and_store(enhanced_profile)
    # ---

    return jsonify({
        "message": f"Source '{source_type}' processed successfully.",
        "enhanced_profile": enhanced_profile.model_dump()
    }), 200


# EMBEDDING: The /match endpoint is removed as it depends on the embedding service.
# ---
# @app.route('/match', methods=['POST'])
# def match_profiles():
#     ...
# ---


# ==============================================================================
# --- Main Execution Block ---
# ==============================================================================

if __name__ == '__main__':
    # DB: The database creation logic is commented out.
    # ---
    # with app.app_context():
    #     db.create_all()
    # ---
    app.run(debug=True, port=5001)