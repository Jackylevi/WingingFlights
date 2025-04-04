import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
import time
import os
import json # Added for JSON file operations

# --- Configuration (Load from Environment Variables) ---
# THESE ARE STILL NEEDED for the initial check, even in dry run!
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") # Use App Password for Gmail

# Define the temporary file name (must match the one in app.py)
TEMP_SUB_FILE = 'last_submission.json'

# --- Initial Check for Environment Variables ---
# Important: Script will exit if these are not set in the terminal session!
if not all([SERPAPI_KEY, EMAIL_SENDER, EMAIL_PASSWORD]):
    print("ERROR: Missing required environment variables (SERPAPI_KEY, EMAIL_SENDER, EMAIL_PASSWORD)")
    print("Please set them in your terminal session before running.")
    exit(1) # Exit if essential config is missing
# ---------------------------------------------

# --- Define Airports ---
# Consider making these configurable or dynamic
DEFAULT_EUROPEAN_AIRPORTS = [
    "LHR", "CDG", "AMS", "FRA", "MUC", "MAD", "BCN", "FCO", "DUB", "ZRH",
    "CPH", "OSL", "ARN", "HEL", "VIE", "BRU", "LIS", "ATH", "PRG", "BUD"
] # Add more as needed


# --- Modified Flight Data Function (DRY RUN VERSION) ---
def get_flight_data_for_user(origin, destinations, max_price, min_days, max_days):
    """Fetches flight data based on user criteria. (DRY RUN VERSION)"""
    today = datetime.now()
    results = [] # This will remain empty in dry run
    print(f"DRY RUN: Simulating search for {origin} -> {destinations or 'Default Europe'} (${max_price}, {min_days}-{max_days} days)")

    # --- Configuration for Dry Run ---
    DRY_RUN_CALL_LIMIT = 50 # Limit how many potential calls we print
    call_counter = 0
    # ---------------------------------

    if not destinations or destinations == 'EUROPE': # Handle default case
        destinations_to_search = DEFAULT_EUROPEAN_AIRPORTS
    else:
        # Assuming 'destinations' might be a list stored for the user in future
        destinations_to_search = destinations if isinstance(destinations, list) else [destinations]

    if origin == "NYC": # Allow searching across major NYC airports
        origins_to_search = ["JFK", "EWR", "LGA"]
    else:
        origins_to_search = [origin]

    # --- Start of the main loops ---
    for dep_airport in origins_to_search:
        for dest_airport in destinations_to_search:
            for departure_offset in range(1, 180): # Check departures for the next ~6 months
                # --- Early exit if limit reached ---
                if call_counter >= DRY_RUN_CALL_LIMIT:
                    print(f"\n--- DRY RUN LIMIT REACHED ({DRY_RUN_CALL_LIMIT}) ---")
                    return results # Exit the function early
                # ----------------------------------

                depart_date = today + timedelta(days=departure_offset)
                for days_delta in range(min_days, max_days + 1):
                    # --- Early exit if limit reached ---
                    if call_counter >= DRY_RUN_CALL_LIMIT:
                        print(f"\n--- DRY RUN LIMIT REACHED ({DRY_RUN_CALL_LIMIT}) ---")
                        return results # Exit the function early
                    # ----------------------------------

                    return_date = depart_date + timedelta(days=days_delta)

                    params = {
                        # Use placeholder in print, actual key isn't sent in dry run
                        "api_key": "YOUR_SERPAPI_KEY_WOULD_BE_HERE",
                        "engine": "Google Flights",
                        "departure_id": dep_airport,
                        "arrival_id": dest_airport,
                        "outbound_date": depart_date.strftime("%Y-%m-%d"),
                        "return_date": return_date.strftime("%Y-%m-%d"),
                        "currency": "USD",
                        "type": "1",  # Roundtrip
                    }

                    # --- DRY RUN PRINT ---
                    print(f"\n[{call_counter + 1}] Would call SerpApi with params:")
                    print(params)
                    call_counter += 1
                    # ---------------------

                    # --- ACTUAL API CALL COMMENTED OUT ---
                    # try:
                    #     response = requests.get("https://serpapi.com/search", params=params, timeout=20)
                    #     response.raise_for_status()
                    #     data = response.json()
                    # except requests.exceptions.RequestException as e:
                    #     pass
                    # except Exception as e:
                    #     pass
                    # --------------------------------------

    print(f"\n--- DRY RUN FINISHED (Looped through all combinations or hit limit) ---")
    return results # Return empty list as no data was fetched


# --- Modified Email Function (Not used in Dry Run but kept for structure) ---
def send_flight_deals_email(receiver_email, flights):
    """Sends an email with the found flight deals."""
    # This function won't be effectively called in dry run mode
    # unless you modify run_checks() further.
    if not flights:
        print(f"DRY RUN: Would check for email sending, but no flights found for {receiver_email}.")
        return
    else:
        print(f"DRY RUN: Would send email with {len(flights)} flights to {receiver_email}.")
        # Actual email sending logic is below but won't run without 'flights' data
        subject = f"✈️ [DRY RUN] WingingFlights Deals Found for {receiver_email}!"
        body = f"Hello!\n\nThis is a DRY RUN. If this were real, deals would be listed here.\n"
        # ... (rest of the email body formatting) ...

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = receiver_email
        print(f"DRY RUN: Email details:\nSubject: {subject}\nTo: {receiver_email}")
        # --- ACTUAL EMAIL SENDING COMMENTED OUT ---
        # try:
        #     with smtplib.SMTP("smtp.gmail.com", 587) as server:
        #         server.starttls()
        #         server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        #         server.send_message(msg)
        #     print(f"DRY RUN: Would have attempted sending email to {receiver_email}")
        # except Exception as e:
        #     print(f"DRY RUN: Error during simulated email sending to {receiver_email}: {e}")
        # --- ----------------------------- ---


# --- Main Execution Logic (Reads from file) ---
def run_checks():
    """Main function: Reads last submission from file and runs dry run check."""
    print(f"Starting flight checks at {datetime.now()}")

    subscriptions_to_check = [] # Start with an empty list

    # --- Load Subscription from File ---
    try:
        # Use the directory where flight_checker.py is located
        filepath = os.path.join(os.path.dirname(__file__), TEMP_SUB_FILE)
        with open(filepath, 'r') as f:
            sub_data = json.load(f)
        print(f"Successfully loaded submission data from {filepath}")
        # Ensure it's treated as a list with one item for the loop
        subscriptions_to_check = [sub_data]
    except FileNotFoundError:
        print(f"WARNING: Submission file '{filepath}' not found.")
        print("Please run the web form first using 'flask run' to create the file.")
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON from '{filepath}'. File might be corrupted.")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while reading '{filepath}': {e}")
    # ------------------------------------

    if not subscriptions_to_check:
        print("No subscription data loaded. Exiting check.")
        return # Exit if no data was loaded

    # --- Loop through the loaded subscription(s) ---
    for sub in subscriptions_to_check:
        print(f"\nChecking flights based on data from file for: {sub.get('email', 'N/A')}")
        try:
            # Retrieve criteria for the current user FROM THE LOADED DATA
            email = sub['email'] # Assuming 'email' key exists from JSON
            max_price = int(sub['max_price']) # Ensure type is correct
            min_days = int(sub['min_days'])
            max_days = int(sub['max_days'])
            origin = sub['origin_airport']
            # Handle 'destinations' potentially not being in the form/JSON yet
            destinations = sub.get('destinations', 'EUROPE') # Default to EUROPE

            # --- Call the DRY RUN flight check function ---
            found_flights = get_flight_data_for_user(origin, destinations, max_price, min_days, max_days)
            # ---------------------------------------------

            # Email sending function called but won't send real emails in dry run
            send_flight_deals_email(email, found_flights)
            # print(f"Dry run check complete for {email}. Found_flights list is empty in dry run.")

        except KeyError as e:
             print(f"ERROR: Missing expected data key '{e}' in the loaded submission from {TEMP_SUB_FILE}. Check the file content.")
        except ValueError as e:
             print(f"ERROR: Invalid data type for price/days in loaded submission for {sub.get('email', 'N/A')}: {e}")
        except Exception as e:
            print(f"ERROR: An unexpected error occurred processing subscription for {sub.get('email', 'UNKNOWN')}: {e}")
            # Add more detailed error logging here

    print(f"\nFinished flight checks at {datetime.now()}")


# --- Main Execution Call ---
if __name__ == "__main__":
    # This allows running the checker manually for testing
    run_checks()