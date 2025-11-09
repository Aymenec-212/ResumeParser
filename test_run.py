# test_run.py
import json
import os
from cv_extractor import extract_cv_data

# --- CONFIGURATION ---
CV_FILE_PATH = "MAIMOUNI_YOUSSEF_CV.pdf"
OUTPUT_DIR = "output"
OUTPUT_FILENAME = "extracted_data.json"


def main():
    """
    Runs the CV extraction pipeline and saves the results to a JSON file.
    """
    print(f"--- Starting extraction for: {CV_FILE_PATH} ---")
    try:
        # This is the main function call to your module
        extracted_data = extract_cv_data(CV_FILE_PATH)

        print("\n--- ✅ Extraction Complete! ---")

        # --- SAVING THE DATA ---
        # Ensure the output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)

        # Pydantic models have a .model_dump_json() method for easy serialization
        with open(output_path, "w") as f:
            f.write(extracted_data.model_dump_json(indent=2))

        print(f"\nSuccessfully saved extracted data to: {output_path}")

    except FileNotFoundError:
        print(f"Error: The file was not found at '{CV_FILE_PATH}'")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Note: The very first run may be slow as SkillNer initializes its database.
    # Subsequent runs will be much faster.
    main()