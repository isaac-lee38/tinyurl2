from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import os
import string

app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/mydatabase")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Base62 encoding (used to generate short links)
BASE62 = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
BASE = len(BASE62)


def encode_base62(num):
    """Convert an integer to a short Base62 string."""
    if num == 0:
        return BASE62[0]
    encoded = []
    while num:
        num, rem = divmod(num, BASE)
        encoded.append(BASE62[rem])
    return ''.join(reversed(encoded))


# Database Model to Store URLs
class ShortenedURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False, unique=True)
    short_code = db.Column(db.String(10), unique=True)

    def generate_short_code(self):
        self.short_code = encode_base62(self.id)


@app.route("/")
def home():
    return "Welcome to TinyURL! Use /shorten to create short URLs."


@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.json
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    # Check if the URL was already shortened
    existing = ShortenedURL.query.filter_by(original_url=original_url).first()
    if existing:
        return jsonify({"shortened_url": f"http://localhost:5000/{existing.short_code}"})

    # Create a new entry
    new_url = ShortenedURL(original_url=original_url)
    db.session.add(new_url)
    db.session.commit()

    # Generate short code
    new_url.generate_short_code()
    db.session.commit()

    return jsonify({"shortened_url": f"http://localhost:5000/{new_url.short_code}"})

#
@app.route("/<short_code>")
def redirect_to_original(short_code):
    url_entry = ShortenedURL.query.filter_by(short_code=short_code).first()
    if url_entry:
        return redirect(url_entry.original_url, code=302)
    return jsonify({"error": "Shortened URL not found"}), 404

# Get all URLs list in the Database
@app.route("/all", methods=["GET"])
def get_all_urls():
    urls = ShortenedURL.query.all()
    return jsonify([{"original_url": url.original_url, "short_code": url.short_code} for url in urls])


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    app.run(host="0.0.0.0", port=5000)
