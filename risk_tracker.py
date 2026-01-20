"""
Entra ID Risk Tracker: Identity Protection & Monitoring Tool
Description: This script utilizes the Microsoft Graph API to monitor the security 
             posture of identities by detecting real-time user risk levels.
Engineer: Ejike Etolue (Jan 2026)
SC-300 Objective: Plan and implement an identity governance strategy
"""

import requests
from azure.identity import ClientSecretCredential
import config  # Secured credentials from local config.py

# --- 🔐 IDENTITY PROTECTION LAYER ---
# Authenticating via a Service Principal to access high-privilege Identity Protection scopes.
credential = ClientSecretCredential(
    tenant_id=config.TENANT_ID,
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET
)

# Fetching OAuth 2.0 Bearer Token for Microsoft Graph
token = credential.get_token("https://graph.microsoft.com/.default")
headers = {'Authorization': f'Bearer {token.token}'}

def get_risk_report():
    """
    Main Logic: Interrogates the Identity Protection API to retrieve a list of 
    risky users flagged by Microsoft's machine learning algorithms.
    """
    # Endpoint for Entra ID Identity Protection
    url = "https://graph.microsoft.com/v1.0/identityProtection/riskyUsers"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Defensive check for API availability
        risky_users = response.json().get('value', [])
        
        print("\n--- 🚩 HIGH-RISK IDENTITY REPORT ---")
        if not risky_users:
            print("✅ No high-risk users detected in the tenant.")
            return
        
        for user in risky_users:
            # Extracting granular risk metadata for security forensics
            name = user.get('userDisplayName')
            level = user.get('riskLevel')
            state = user.get('riskState')
            print(f"⚠️  {name.ljust(20)} | Level: {level.upper()} | State: {state}")
            
    except Exception as e:
        print(f"❌ Error fetching risk data: {e}")

if __name__ == "__main__":
    get_risk_report()