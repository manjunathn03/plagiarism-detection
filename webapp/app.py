import os
import sys
import logging
import sqlite3
import PyPDF2
import docx
from functools import wraps
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, jsonify, g
)
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------------------------------------
# Configure Logging
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Flask Setup
# -------------------------------------------------
app = Flask(__name__)
app.secret_key = "YOUR_FLASK_SECRET_KEY"  # Replace with your secret key
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "app.db")
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# -------------------------------------------------
# Database Helpers
# -------------------------------------------------
def get_db():
    """Open a new database connection if there is none yet for the current application context."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # so rows behave like dicts
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Closes the database at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database with the 'users' table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def create_user(firstname, lastname, email, password):
    """Insert a new user with hashed password into the 'users' table."""
    conn = get_db()
    cur = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cur.execute("INSERT INTO users (firstname, lastname, email, password_hash) VALUES (?,?,?,?)",
                    (firstname, lastname, email, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Email already exists or another DB constraint error
        return False

def get_user_by_email(email):
    """Return user row from the 'users' table by email, or None if not found."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cur.fetchone()

# -------------------------------------------------
# login_required Decorator
# -------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------------------------
# Routes
# -------------------------------------------------
@app.route("/")
def home():
    """Redirect to /text if logged in, else redirect to /login."""
    if "user_id" in session:
        return redirect(url_for("text_plagiarism_page"))
    return redirect(url_for("login_page"))

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if request.method == "POST":
        firstname = request.form["firstname"].strip()
        lastname = request.form["lastname"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        if not firstname or not lastname or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("signup.html")

        # Create user in the database
        success = create_user(firstname, lastname, email, password)
        if success:
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login_page"))
        else:
            flash("Error: That email is already registered!", "danger")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        if not email or not password:
            flash("All fields are required.", "danger")
            return render_template("login.html")

        user_row = get_user_by_email(email)
        if user_row:
            stored_hash = user_row["password_hash"]
            if check_password_hash(stored_hash, password):
                # Password is correct; set session variables
                session["user_id"] = user_row["id"]
                session["user_email"] = user_row["email"]
                flash("Login successful!", "success")
                return redirect(url_for("text_plagiarism_page"))
            else:
                flash("Incorrect password!", "danger")
        else:
            flash("No user found with that email!", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login_page"))

# -------------------------------------------------
# Protected Plagiarism Routes
# -------------------------------------------------
@app.route("/text")
@login_required
def text_plagiarism_page():
    return render_template("text.html")

@app.route("/image")
@login_required
def image_plagiarism_page():
    return render_template("image.html")

@app.route("/code")
@login_required
def code_plagiarism_page():
    return render_template("code.html")

@app.route("/document")
@login_required
def document_plagiarism_page():
    return render_template("document.html")

# -------------------------------------------------
# Plagiarism Detection Endpoints (Examples)
# -------------------------------------------------
@app.route("/detect_text", methods=["POST"])
@login_required
def detect_text():
    text1 = request.form.get("text1", "")
    text2 = request.form.get("text2", "")
    if not text1 or not text2:
        flash("Both text fields are required!", "danger")
        return redirect(url_for("text_plagiarism_page"))

    similarity = compute_text_similarity(text1, text2)
    plagiarism_percentage = round(similarity * 100, 2)
    return render_template("result.html", method="Text", 
                           similarity=similarity,
                           plagiarism_percentage=plagiarism_percentage)

def compute_text_similarity(a, b):
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    intersect = a_words.intersection(b_words)
    union = a_words.union(b_words)
    return len(intersect) / len(union) if union else 0

@app.route("/detect_image", methods=["POST"])
@login_required
def detect_image():
    if "image1" not in request.files:
        flash("No image uploaded!", "danger")
        return redirect(url_for("image_plagiarism_page"))
    file = request.files["image1"]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)
    plagiarism_results = google_image_search(file_path)
    return render_template("result.html", method="Image", 
                           search_results=plagiarism_results)

@app.route("/detect_code", methods=["POST"])
@login_required
def detect_code():
    code1 = request.form.get("code1", "")
    if not code1:
        flash("Code input is required!", "danger")
        return redirect(url_for("code_plagiarism_page"))
    github_results = search_github_code(code1)
    return render_template("result.html", method="Code", 
                           search_results=github_results.get("items", []))

@app.route("/detect_document", methods=["POST"])
@login_required
def detect_document():
    if "document" not in request.files:
        flash("No document uploaded!", "danger")
        return redirect(url_for("document_plagiarism_page"))
    file = request.files["document"]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)
    extracted_text = extract_text_from_document(file_path)
    if not extracted_text:
        flash("Failed to extract text from document!", "danger")
        return redirect(url_for("document_plagiarism_page"))
    plagiarism_results = google_search(extracted_text[:100])
    return render_template("result.html", method="Document", 
                           search_results=plagiarism_results)

def extract_text_from_document(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    return None

def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return "".join(page.extract_text() for page in reader.pages)

def extract_text_from_docx(file_path):
    return " ".join(para.text for para in docx.Document(file_path).paragraphs)

def google_image_search(file_path):
    # Dummy placeholder
    return ["Example image result 1", "Example image result 2"]

def search_github_code(query):
    # Dummy placeholder
    return {"items": [{"name": "Example code snippet"}]}

def google_search(query):
    # Dummy placeholder
    return ["Example search result 1", "Example search result 2"]

# -------------------------------------------------
# Run the Application
# -------------------------------------------------
if __name__ == "__main__":
    init_db()  # Initialize the database (creates table if needed)
    app.run(debug=True)
