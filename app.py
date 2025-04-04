# app.py
import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, render_template
import sqlite3 # Import sqlite3
import json # Keep json import if needed elsewhere, otherwise optional

app = Flask(__name__)

# Define the database file path relative to app.py
DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'database.db')

# --- Helper Function for Database Connection (Optional but good practice) ---
def get_db_connection():
    """Creates a database connection."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row # Return rows as dictionary-like objects
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

# --- Helper Function to Send Confirmation Email (Keep the HTML version from before) ---
def send_confirmation_email(submission_data):
    # ... (Keep the full HTML email sending function code from the previous step here) ...
    # ... (Make sure it correctly gets email/password from environment variables) ...
    receiver_email = submission_data.get('email')
    if not receiver_email:
        print("ERROR: Cannot send confirmation, email missing in submission data.")
        return False # Indicate failure
    email_sender = os.environ.get('EMAIL_SENDER')
    email_password = os.environ.get('EMAIL_PASSWORD')
    if not email_sender or not email_password:
        print("WARNING: Email credentials not found. Confirmation email NOT sent.")
        return False
    subject = "WingingFlights Subscription Confirmed!"
    html_body = f"""
<!DOCTYPE html><html><head><style>body {{ font-family: sans-serif; line-height: 1.6; }} .container {{ padding: 20px; border: 1px solid #eee; max-width: 600px; margin: auto; }} .criteria-list li {{ margin-bottom: 5px; }} strong {{ color: #333; }}</style></head><body><div class="container">
<p>Hello {receiver_email},</p><p>Thanks for subscribing to WingingFlights!</p><p>This email confirms the criteria we have saved:</p><hr><ul class="criteria-list">
<li><strong>Email:</strong> {submission_data.get('email')}</li><li><strong>Max Price:</strong> ${submission_data.get('max_price', 'N/A')}</li><li><strong>Min Trip Days:</strong> {submission_data.get('min_days', 'N/A')}</li><li><strong>Max Trip Days:</strong> {submission_data.get('max_days', 'N/A')}</li><li><strong>Departure Airport:</strong> {submission_data.get('origin_airport', 'N/A')}</li></ul><hr>
<p>Based on these selections, you will receive daily emails (when deals are found).</p><p><strong>Need to change your criteria?</strong><br>Simply visit the subscription page again and submit the form with your updated information.</p><p>Happy Travels!</p><p>- The WingingFlights Team<br><small>(This is an automated message)</small></p></div></body></html>"""
    msg = MIMEText(html_body, 'html')
    msg["Subject"] = subject; msg["From"] = email_sender; msg["To"] = receiver_email
    print(f"Attempting to send HTML confirmation email to {receiver_email}...")
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(); server.login(email_sender, email_password); server.send_message(msg)
        print(f"HTML Confirmation email sent successfully to {receiver_email}"); return True
    except smtplib.SMTPAuthenticationError: print(f"ERROR sending email: Authentication failed."); return False
    except Exception as e: print(f"ERROR sending confirmation email: {e}"); return False


# --- Routes ---
@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Handles subscription requests, saves/updates in DB, sends confirmation email."""
    data = request.get_json()
    if not data: return jsonify({"error": "Invalid input format"}), 400

    # --- Validation ---
    email = data.get('email')
    max_price = data.get('max_price')
    min_days = data.get('min_days')
    max_days = data.get('max_days')
    origin_airport = data.get('origin_airport')
    if not all([email, max_price, min_days, max_days, origin_airport]):
        return jsonify({"error": "Missing required fields"}), 400
    try:
        max_price = int(max_price)
        min_days = int(min_days)
        max_days = int(max_days)
        if min_days > max_days or max_price <= 0 or min_days <= 0: raise ValueError("Invalid numeric values")
        # Update data dict with converted types for email function
        data['max_price'] = max_price
        data['min_days'] = min_days
        data['max_days'] = max_days
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data types for price or days"}), 400
    # --- End Validation ---

    print("Received Subscription Data:", data) # Keep for debugging

    # --- Save/Update Subscription Data in SQLite DB ---
    conn = None # Initialize conn outside try
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Use INSERT OR REPLACE to handle both new and existing emails
            # If email exists, it replaces the entire row; if not, it inserts.
            cursor.execute('''
                INSERT OR REPLACE INTO subscriptions (email, max_price, min_days, max_days, origin_airport)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, max_price, min_days, max_days, origin_airport))
            conn.commit()
            print(f"Successfully saved/updated subscription for {email} in database.")
        else:
             # Handle connection error - maybe return an error to user
             return jsonify({"error": "Database connection failed"}), 500

    except sqlite3.Error as e:
        print(f"ERROR: Database error during save/update for {email}: {e}")
        return jsonify({"error": "Failed to save subscription data due to database error"}), 500
    except Exception as e:
         print(f"ERROR: An unexpected error occurred during database operation: {e}")
         return jsonify({"error": "An unexpected error occurred while saving data"}), 500
    finally:
        if conn:
            conn.close() # Make sure connection is closed
    # -------------------------------------------------

    # --- Attempt to Send Confirmation Email (using original 'data' dict) ---
    email_sent = send_confirmation_email(data)
    # ------------------------------------------

    response_message = f"Successfully subscribed {email}! Data saved."
    if email_sent:
        response_message += " Check your inbox for confirmation."
    else:
        response_message += " (Confirmation email failed to send)."

    return jsonify({"message": response_message}), 200

# --- Main Execution ---
if __name__ == '__main__':
    print("Checking database on startup...")
    # Optional: Run init logic here if you prefer not having a separate script
    # init_db() # Assuming init_db is defined within this file or imported
    print(f"Database file expected at: {DATABASE_FILE}")
    if not os.path.exists(DATABASE_FILE):
         print("WARNING: Database file not found. Please run init_db.py first!")
    app.run(debug=True, host='0.0.0.0')