# app.py
import os
import uuid
from threading import Thread
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# --- Import all your self-contained extractor functions ---
from cv_extractor import extract_cv_data
from github_extractor.api_client import get_profile_from_github_url
from linkedin_extractor.scraper import collect_profile_from_linkedin_url

# ==============================================================================
# --- App Configuration ---
# ==============================================================================

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- In-Memory Job Store ---
# NOTE: This is for simplicity. In a production environment, you would replace
# this with a more robust solution like Redis or a database.
JOBS = {}


# Example structure:
# { "job-id-123": {"status": "pending"},
#   "job-id-456": {"status": "completed", "result": {...}} }


def allowed_file(filename):
    """Checks if a file's extension is in the ALLOWED_EXTENSIONS set."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==============================================================================
# --- Generic Background Task Runner ---
# ==============================================================================

def run_extraction_task(job_id, extractor_func, **kwargs):
    """
    A generic worker function that runs any given extractor and updates the job store.
    """
    print(f"Starting background task for job_id: {job_id}")
    try:
        # Run the provided extractor function with its arguments
        result_pydantic = extractor_func(**kwargs)

        # Convert the Pydantic model to a dictionary for JSON serialization
        result_dict = result_pydantic.model_dump()

        # Update the job store with the final result
        JOBS[job_id] = {"status": "completed", "result": result_dict}
        print(f"Successfully completed job_id: {job_id}")

    except Exception as e:
        print(f"Error processing job_id {job_id}: {e}")
        # Update the job store with the error message
        JOBS[job_id] = {"status": "error", "message": str(e)}


# ==============================================================================
# --- API Endpoints ---
# ==============================================================================

@app.route('/extract', methods=['POST'])
def start_extraction():
    """
    A single, unified endpoint to start any extraction job.
    The client specifies the 'source_type' in the form data.
    """
    source_type = request.form.get('source_type')
    if not source_type:
        return jsonify({"error": "Missing 'source_type' (must be 'cv', 'linkedin', or 'github')"}), 400

    job_id = str(uuid.uuid4())
    extractor_func = None
    kwargs = {}

    # --- Dispatcher: Choose the right extractor based on source_type ---
    if source_type == 'cv':
        if 'file' not in request.files:
            return jsonify({"error": "No file part for 'cv' source_type"}), 400
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({"error": "Invalid or missing file for 'cv' source_type"}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        extractor_func = extract_cv_data
        kwargs = {'file_path': filepath}

    elif source_type == 'linkedin':
        url = request.form.get('url')
        if not url:
            return jsonify({"error": "Missing 'url' for 'linkedin' source_type"}), 400
        extractor_func = collect_profile_from_linkedin_url
        kwargs = {'url': url}

    elif source_type == 'github':
        url = request.form.get('url')
        if not url:
            return jsonify({"error": "Missing 'url' for 'github' source_type"}), 400
        extractor_func = get_profile_from_github_url
        kwargs = {'url': url}

    else:
        return jsonify({"error": f"Invalid source_type: '{source_type}'"}), 400

    # --- Start the generic background job ---
    JOBS[job_id] = {"status": "pending"}
    thread = Thread(target=run_extraction_task, args=(job_id, extractor_func), kwargs=kwargs)
    thread.start()

    return jsonify({
        "message": f"{source_type.capitalize()} processing started.",
        "job_id": job_id
    }), 202


@app.route('/status/<string:job_id>', methods=['GET'])
def get_job_status(job_id):
    """
    A single endpoint to check the status or get the result of any job.
    """
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job ID not found"}), 404

    return jsonify(job)


if __name__ == '__main__':
    app.run(debug=True, port=5001)