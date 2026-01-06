import csv
from datetime import datetime

# --- SETTINGS ---
# DRY_RUN = True means we only simulate the process. 
# Set to False only when ready to push changes to the live cloud.
DRY_RUN = True  

def log_event(message):
    """
    Captures a message and saves it to a local text file with a timestamp.
    'a' mode ensures we append to the file rather than overwriting it.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("execution_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def process_users(filename):
    """Reads user data from CSV and performs validation logic."""
    print(f"--- 🚀 Starting Lab (Dry Run: {DRY_RUN}) ---")
    log_event(f"PROCESS STARTED. Dry Run: {DRY_RUN}")
    
    try:
        # Open the CSV file for reading
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Logic Gate: Check if the required email field is populated
                if not row['userPrincipalName']:
                    msg = f"⚠️ [SKIP] Missing email for: {row['displayName']}"
                    print(msg)
                    log_event(msg) # Log the error for later audit
                    continue 
                
                # If validation passes, prepare for creation
                msg = f"✅ Ready to create: {row['displayName']} at {row['usageLocation']}"
                print(msg)
                log_event(msg)

    except FileNotFoundError:
        error_msg = f"❌ Error: {filename} not found."
        print(error_msg)
        log_event(error_msg)

# This block checks if the script is being run directly by the user.
# If it is, it triggers the 'process_users' function.
if __name__ == "__main__":
    process_users('users.csv')