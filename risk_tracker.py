import requests
from azure.identity import ClientSecretCredential
import config

credential = ClientSecretCredential(
    tenant_id=config.TENANT_ID,
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET
)

token = credential.get_token("https://graph.microsoft.com/.default")
headers = {'Authorization': f'Bearer {token.token}'}

def get_risk_report():
    # Endpoint for Entra ID Identity Protection
    url = "https://graph.microsoft.com/v1.0/identityProtection/riskyUsers"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        risky_users = response.json().get('value', [])
        
        print("\n--- 🚩 HIGH-RISK IDENTITY REPORT ---")
        if not risky_users:
            print("✅ No high-risk users detected in the tenant.")
        
        for user in risky_users:
            name = user.get('userDisplayName')
            level = user.get('riskLevel')
            state = user.get('riskState')
            print(f"⚠️  {name.ljust(20)} | Level: {level.upper()} | State: {state}")
            
    except Exception as e:
        print(f"❌ Error fetching risk data: {e}")

if __name__ == "__main__":
    get_risk_report()