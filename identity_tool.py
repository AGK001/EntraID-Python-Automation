import csv
import asyncio
import config
from datetime import datetime
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.user import User
from msgraph.generated.models.password_profile import PasswordProfile

# --- AUTHENTICATION ---
# Using ClientSecretCredential for Application permissions
credential = ClientSecretCredential(
    tenant_id=config.TENANT_ID,
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET
)
client = GraphServiceClient(credential)

def log_event(message):
    """Saves progress to a text file with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("execution_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

async def create_entra_user(display_name, nickname, upn, location, password):
    """Translates Python data into a Microsoft Graph User object."""
    new_user = User(
        display_name=display_name,
        mail_nickname=nickname,
        user_principal_name=upn,
        usage_location=location,
        account_enabled=True,
        password_profile=PasswordProfile(
            force_change_password_next_sign_in=True,
            password=password
        )
    )
    # This sends the 'POST' request to create the user in your tenant
    await client.users.post(new_user)

async def main():
    print("--- 🚀 Starting LIVE Identity Automation ---")
    log_event("SESSION START: Live Cloud Integration.")
    
    try:
        with open('users.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Skip invalid data (Our 'Invalid User' test)
                if not row['userPrincipalName']:
                    msg = f"⚠️ [SKIP] Invalid data for: {row['displayName']}"
                    print(msg)
                    log_event(msg)
                    continue
                
                # Execute Cloud Creation
                try:
                    print(f"🔗 Connecting to Cloud for: {row['displayName']}...")
                    await create_entra_user(
                        row['displayName'], 
                        row['mailNickname'], 
                        row['userPrincipalName'], 
                        row['usageLocation'], 
                        row['password']
                    )
                    success_msg = f"✅ SUCCESS: {row['displayName']} created in Entra ID."
                    print(success_msg)
                    log_event(success_msg)
                except Exception as e:
                    error_msg = f"❌ FAILED to create {row['displayName']}: {e}"
                    print(error_msg)
                    log_event(error_msg)

    except FileNotFoundError:
        print("❌ Error: users.csv not found.")
        log_event("CRITICAL ERROR: users.csv missing.")

if __name__ == "__main__":
    # asyncio allows the script to stay "awake" and ready to handle multiple tasks at once
    asyncio.run(main())