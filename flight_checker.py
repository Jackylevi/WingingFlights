# flight_checker.py
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import time
import os
import json # Keep for potential future use? Otherwise optional
import sqlite3 # Import sqlite3

# --- Configuration & Environment Variable Checks ---
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'database.db')

if not all([SERPAPI_KEY, EMAIL_SENDER, EMAIL_PASSWORD]):
    print("ERROR: Missing required environment variables (SERPAPI_KEY, EMAIL_SENDER, EMAIL_PASSWORD)")
    exit(1)
if not os.path.exists(DATABASE_FILE):
    print(f"ERROR: Database file not found at {DATABASE_FILE}. Run init_db.py first.")
    exit(1)
# ---------------------------------------------

# --- Define Airports (Keep as is) ---
DEFAULT_EUROPEAN_AIRPORTS = [
    "LHR", "CDG", "AMS", "FRA", "MUC", "MAD", "BCN", "FCO", "DUB", "ZRH",
    "CPH", "OSL", "ARN", "HEL", "VIE", "BRU", "LIS", "ATH", "PRG", "BUD"
]

# --- Flight Data Function (Keep DRY RUN Version from before) ---
def get_flight_data_for_user(origin, destinations, max_price, min_days, max_days):
    # ... (Keep the full DRY RUN version of this function here) ...
    # ... (It prints potential API calls but returns []) ...
    today = datetime.now(); results = []; print(f"DRY RUN: Simulating search for {origin} -> {destinations or 'Default Europe'} (${max_price}, {min_days}-{max_days} days)")
    DRY_RUN_CALL_LIMIT = 50; call_counter = 0
    if not destinations or destinations == 'EUROPE': destinations_to_search = DEFAULT_EUROPEAN_AIRPORTS
    else: destinations_to_search = destinations if isinstance(destinations, list) else [destinations]
    if origin == "NYC": origins_to_search = ["JFK", "EWR", "LGA"]
    else: origins_to_search = [origin]
    for dep_airport in origins_to_search:
        for dest_airport in destinations_to_search:
            for departure_offset in range(1, 180): # Shorten range (e.g., 1, 5) to reduce dry run output if needed
                if call_counter >= DRY_RUN_CALL_LIMIT: print(f"\n--- DRY RUN LIMIT REACHED ({DRY_RUN_CALL_LIMIT}) ---"); return results
                depart_date = today + timedelta(days=departure_offset)
                for days_delta in range(min_days, max_days + 1):
                    if call_counter >= DRY_RUN_CALL_LIMIT: print(f"\n--- DRY RUN LIMIT REACHED ({DRY_RUN_CALL_LIMIT}) ---"); return results
                    return_date = depart_date + timedelta(days=days_delta)
                    params = {"api_key": "DRY_RUN_KEY", "engine": "Google Flights", "departure_id": dep_airport, "arrival_id": dest_airport, "outbound_date": depart_date.strftime("%Y-%m-%d"), "return_date": return_date.strftime("%Y-%m-%d"), "currency": "USD", "type": "1"}
                    print(f"\n[{call_counter + 1}] Would call SerpApi with params:"); print(params); call_counter += 1
                    # --- ACTUAL API CALL COMMENTED OUT ---
    print(f"\n--- DRY RUN FINISHED (Looped or hit limit) ---"); return results

# --- Daily Deals Email Function (Keep HTML version sending FAKE deals) ---
def send_flight_deals_email(receiver_email, flights, user_criteria):
    # ... (Keep the full HTML email sending function from the previous step here) ...
    # ... (It should take fake 'flights' list and format/send the email) ...
    email_sender = os.environ.get('EMAIL_SENDER'); email_password = os.environ.get('EMAIL_PASSWORD')
    if not email_sender or not email_password: print("WARNING: Email credentials not found. Daily deals email NOT sent."); return False
    subject = f"✈️ WingingFlights Deals Matching Your Criteria!"; deals_html = ""
    if not flights: print(f"No flights (real or fake) provided for {receiver_email}. No email sent."); return False
    else:
        deals_html += "<ul>";
        for flight in flights: deals_html += f"""<li style="margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;"><strong>From:</strong> {flight.get('origin', 'N/A')} -> <strong>To:</strong> {flight.get('destination', 'N/A')}<br><strong>Price:</strong> ${flight.get('price', 'N/A')}<br><strong>Dates:</strong> {flight.get('departure_date', 'N/A')} to {flight.get('return_date', 'N/A')} ({flight.get('trip_length', 'N/A')} days)<br><a href='{flight.get('Google Flights_url', '#')}'>View Deal (Example Link)</a></li>"""
        deals_html += "</ul>"
    html_body = f"""<!DOCTYPE html><html><head><style>body {{ font-family: sans-serif; line-height: 1.6; }} .container {{ padding: 20px; border: 1px solid #eee; max-width: 600px; margin: auto; }} strong {{ color: #333; }} ul {{ list-style: none; padding: 0; }}</style></head><body><div class="container">
<p>Hello {receiver_email},</p><p>Here are the latest flight deals we found matching your criteria:</p><p>(Max Price: ${user_criteria.get('max_price', 'N/A')}, Min Days: {user_criteria.get('min_days', 'N/A')}, Max Days: {user_criteria.get('max_days', 'N/A')}, Origin: {user_criteria.get('origin_airport', 'N/A')})</p><hr>{deals_html}<hr>
<p><small>Note: Prices/availability change rapidly. Example links.</small></p><p>Happy Travels!</p><p>- The WingingFlights Team</p></div></body></html>"""
    msg = MIMEText(html_body, 'html'); msg["Subject"] = subject; msg["From"] = email_sender; msg["To"] = receiver_email
    print(f"Attempting to send deals email to {receiver_email}...")
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server: server.starttls(); server.login(email_sender, email_password); server.send_message(msg)
        print(f"Deals email sent successfully to {receiver_email}"); return True
    except smtplib.SMTPAuthenticationError: print(f"ERROR sending email: Authentication failed."); return False
    except Exception as e: print(f"ERROR sending deals email: {e}"); return False


# --- Main Execution Logic (Reads ALL users from DB, makes FAKE deals) ---
def run_checks():
    """Reads ALL subscriptions from DB, runs dry run check, creates FAKE deals, sends deals email for EACH user."""
    print(f"Starting flight checks at {datetime.now()} - Reading from SQLite DB.")

    all_subscriptions = []
    conn = None
    # --- Load ALL Subscriptions from Database ---
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        # Use a dictionary cursor for easier access by column name
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT email, max_price, min_days, max_days, origin_airport FROM subscriptions")
        all_subscriptions = cursor.fetchall() # Fetch all rows
        print(f"Found {len(all_subscriptions)} subscriptions in the database.")
    except sqlite3.Error as e:
        print(f"ERROR reading subscriptions from database: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while reading database: {e}")
    finally:
        if conn:
            conn.close()
    # -------------------------------------------

    if not all_subscriptions:
        print("No active subscriptions found in database. Exiting check.")
        return

    # --- Loop through EACH subscription from the database ---
    for sub_row in all_subscriptions:
        # Convert the sqlite3.Row object to a dictionary for consistent use
        sub_criteria = dict(sub_row)
        email = sub_criteria.get('email')
        if not email:
            print("Skipping row with missing email.")
            continue

        print(f"\n--- Processing criteria for: {email} ---")
        try:
            # Ensure types are correct (they should be from DB, but double-check)
            max_price = int(sub_criteria['max_price'])
            min_days = int(sub_criteria['min_days'])
            max_days = int(sub_criteria['max_days'])
            origin = sub_criteria['origin_airport']
            destinations = sub_criteria.get('destinations', 'EUROPE') # 'destinations' isn't in DB yet

            # --- Call the DRY RUN flight check function ---
            print(f"Performing DRY RUN check for potential API calls for {email}...")
            _ = get_flight_data_for_user(origin, destinations, max_price, min_days, max_days)
            print(f"Dry run check complete for {email}.")
            # ---------------------------------------------

            # --- !!! CREATE FAKE FLIGHT DATA for this user !!! ---
            print(f"Generating placeholder flight deals for {email}...")
            fake_flights = [
                {
                    "origin": origin, "destination": "LHR", "price": max_price - 30,
                    "departure_date": (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d'),
                    "return_date": (datetime.now() + timedelta(days=45 + min_days)).strftime('%Y-%m-%d'),
                    "trip_length": min_days, "Google Flights_url": "https://www.google.com/flights"
                },
                 { # Add another fake deal potentially outside price range to test filter
                    "origin": origin, "destination": "AMS", "price": max_price + 50,
                    "departure_date": (datetime.now() + timedelta(days=75)).strftime('%Y-%m-%d'),
                    "return_date": (datetime.now() + timedelta(days=75 + max_days)).strftime('%Y-%m-%d'),
                    "trip_length": max_days, "Google Flights_url": "https://www.google.com/flights"
                }
            ]
            # Filter fake flights just in case price was generated above max_price
            fake_flights_filtered = [f for f in fake_flights if f.get('price', float('inf')) <= max_price]
            print(f"Created {len(fake_flights_filtered)} fake deals meeting criteria for {email}.")
            # --- End Fake Data Creation ---

            # --- Send the Email with FAKE Deals ---
            if fake_flights_filtered:
                 send_flight_deals_email(email, fake_flights_filtered, sub_criteria)
            else:
                 print(f"No fake deals generated meeting criteria for {email}, skipping email.")
            # --------------------------------------

        except KeyError as e:
             print(f"ERROR: Missing expected data key '{e}' in database row for {email}.")
        except ValueError as e:
             print(f"ERROR: Invalid data type for price/days in database row for {email}: {e}")
        except Exception as e:
            print(f"ERROR processing subscription for {email}: {e}")

    print(f"\nFinished processing all subscriptions at {datetime.now()}")

# --- Main Execution Call ---
if __name__ == "__main__":
    run_checks()