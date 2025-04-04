import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, render_template
import json # Added for JSON file operations

app = Flask(__name__)

# Define the temporary file name
TEMP_SUB_FILE = 'last_submission.json'

def send_confirmation_email(submission_data):
    """Sends a confirmation email with submission details, formatted as HTML."""
    receiver_email = submission_data.get('email')
    if not receiver_email:
        print("ERROR: Cannot send confirmation, email missing in submission data.")
        return False # Indicate failure

    # --- Get Email Credentials ---
    email_sender = os.environ.get('EMAIL_SENDER')
    email_password = os.environ.get('EMAIL_PASSWORD') # Use App Password for Gmail

    if not email_sender or not email_password:
        print("WARNING: Email credentials (EMAIL_SENDER, EMAIL_PASSWORD) not found in environment variables.")
        print("Confirmation email will NOT be sent.")
        return False # Indicate failure
    # -----------------------------

    subject = "WingingFlights Subscription Confirmed!"

    # --- Create HTML Body ---
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ font-family: sans-serif; line-height: 1.6; }}
    .container {{ padding: 20px; border: 1px solid #eee; max-width: 600px; margin: auto; }}
    .criteria-list li {{ margin-bottom: 5px; }}
    strong {{ color: #333; }}
</style>
</head>
<body>
    <div class="container">
        <p>Hello {receiver_email},</p>

        <p>Thanks for subscribing to WingingFlights! We saw you filled out our form.</p>

        <p>This email confirms the criteria we have saved for your daily flight alerts:</p>
        <hr>
        <ul class="criteria-list">
            <li><strong>Email:</strong> {submission_data.get('email')}</li>
            <li><strong>Max Price:</strong> ${submission_data.get('max_price', 'N/A')}</li>
            <li><strong>Min Trip Days:</strong> {submission_data.get('min_days', 'N/A')}</li>
            <li><strong>Max Trip Days:</strong> {submission_data.get('max_days', 'N/A')}</li>
            <li><strong>Departure Airport:</strong> {submission_data.get('origin_airport', 'N/A')}</li>
        </ul>
        <hr>

        <p>Based on these selections, you will receive daily emails (when deals are found) about roundtrip flights from NYC to Europe that fit your criteria.</p>

        <p><strong>Need to change your criteria?</strong><br>
           Simply visit the subscription page again and submit the form with your updated information. Only your most recent submission is used.</p>

        <p>Happy Travels!</p>

        <p>- The WingingFlights Team<br>
           <small>(This is an automated message)</small>
        </p>
    </div>
</body>
</html>
"""
    # --- End HTML Body ---

    # Create the email message, specifying 'html' subtype
    msg = MIMEText(html_body, 'html')
    msg["Subject"] = subject
    msg["From"] = email_sender
    msg["To"] = receiver_email

    print(f"Attempting to send HTML confirmation email to {receiver_email}...")
    try:
        # Connect to Gmail's SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls() # Secure the connection
            server.login(email_sender, email_password)
            server.send_message(msg)
        print(f"HTML Confirmation email sent successfully to {receiver_email}")
        return True # Indicate success
    except smtplib.SMTPAuthenticationError:
        print(f"ERROR sending email: Authentication failed. Check EMAIL_SENDER and EMAIL_PASSWORD (use App Password for Gmail).")
        return False
    except Exception as e:
        print(f"ERROR sending confirmation email to {receiver_email}: {e}")
        return False # Indicate failure

# --- Routes ---

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Handles subscription requests, saves to file, and sends confirmation email."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid input format"}), 400

    # --- Validation (Keep as is) ---
    email = data.get('email')
    max_price = data.get('max_price')
    min_days = data.get('min_days')
    max_days = data.get('max_days')
    origin_airport = data.get('origin_airport')
    if not all([email, max_price, min_days, max_days, origin_airport]):
        return jsonify({"error": "Missing required fields"}), 400
    try:
        data['max_price'] = int(max_price)
        data['min_days'] = int(min_days)
        data['max_days'] = int(max_days)
        if data['min_days'] > data['max_days'] or data['max_price'] <= 0 or data['min_days'] <= 0:
             raise ValueError("Invalid numeric values")
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data types for price or days"}), 400
    # --- End Validation ---

    print("Received Subscription Data:", data) # Keep for debugging

    # --- Save Subscription Data to File ---
    try:
        filepath = os.path.join(os.path.dirname(__file__), TEMP_SUB_FILE)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully saved submission to {filepath}")
    except Exception as e:
        print(f"ERROR: Could not write to file {filepath}: {e}")
        return jsonify({"error": "Failed to save subscription data"}), 500
    # ------------------------------------

    # --- Attempt to Send Confirmation Email ---
    email_sent = send_confirmation_email(data)
    # ------------------------------------------

    # Customize response message based on email success (optional)
    if email_sent:
        response_message = f"Successfully subscribed {email}! Check your inbox for confirmation. Data saved for next dry run."
    else:
        response_message = f"Successfully subscribed {email}! (Confirmation email failed to send). Data saved for next dry run."

    return jsonify({"message": response_message}), 200


# --- Main Execution ---
if __name__ == '__main__':
    # Remember to set environment variables before running!
    app.run(debug=True, host='0.0.0.0') # debug=True is NOT for production