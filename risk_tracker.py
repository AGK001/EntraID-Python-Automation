"""
Entra ID Risk Tracker: Identity Protection & Monitoring Tool
Description: This script utilizes the Microsoft Graph API to monitor the security 
             posture of identities by detecting real-time user risk levels and reasons.
Engineer: Ejike Etolue (Jan 2026)
SC-300 Objective: Plan and implement an identity governance strategy
"""

import requests
from azure.identity import ClientSecretCredential
import config  # Secured credentials from local config.py

# --- 🔐 IDENTITY PROTECTION LAYER ---
credential = ClientSecretCredential(
    tenant_id=config.TENANT_ID,
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET
)

token = credential.get_token("https://graph.microsoft.com/.default")
headers = {'Authorization': f'Bearer {token.token}'}

def get_risk_report():
    """
    Main Logic: Interrogates the Identity Protection API to retrieve a list of 
    risky users and parses nested JSON to extract the specific risk reason.
    """
    url = "https://graph.microsoft.com/v1.0/identityProtection/riskyUsers"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        risky_users = response.json().get('value', [])
        
        print("\n--- 🚩 HIGH-RISK IDENTITY REPORT ---")
        if not risky_users:
            print("✅ No high-risk users detected in the tenant.")
            return

        # Professional Table Header for the "Identity Report" Milestone
        print(f"{'USER':<20} | {'LEVEL':<10} | {'STATE':<12} | {'RISK REASON'}")
        print("-" * 70)
        
        for user in risky_users:
            name = user.get('userDisplayName', 'Unknown')
            level = user.get('riskLevel', 'low').upper()
            state = user.get('riskState', 'none')
            
            # Extracting the "Why": Handling the riskDetail enum
            detail = user.get('riskDetail', 'none')
            
            # Formatting the reason for better readability in the report
            reason = "Awaiting Investigation" if detail == "none" else detail
            
            print(f"{name:<20} | {level:<10} | {state:<12} | {reason}")
            
    except Exception as e:
        print(f"❌ Error fetching risk data: {e}")

if __name__ == "__main__":
    get_risk_report()