"""
Entra ID Risk Tracker: Identity Protection & Monitoring Tool
Description: Programmatically interrogates the Microsoft Graph API to monitor 
             identity security posture and detect anomalous user behavior.
Engineer: Ejike Etolue (January 2026)
SC-300 Objective: Implement an identity governance and protection strategy.
"""

import requests
from azure.identity import ClientSecretCredential
import config 

# --- SERVICE PRINCIPAL AUTHENTICATION ---
credential = ClientSecretCredential(
    tenant_id=config.TENANT_ID,
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET
)

token = credential.get_token("https://graph.microsoft.com/.default")
headers = {'Authorization': f'Bearer {token.token}'}

def get_risk_report():
    """
    Fetches risky user data from Entra Identity Protection and parses 
    nested JSON properties for forensic reporting.
    """
    url = "https://graph.microsoft.com/v1.0/identityProtection/riskyUsers"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        risky_users = response.json().get('value', [])
        
        print("\n--- IDENTITY PROTECTION: HIGH-RISK REPORT ---")
        if not risky_users:
            print("✅ Status: No high-risk users detected.")
            return

        # Initialize reporting table structure
        print(f"{'USER':<20} | {'LEVEL':<10} | {'STATE':<12} | {'RISK DETAIL'}")
        print("-" * 70)
        
        for user in risky_users:
            name = user.get('userDisplayName', 'Unknown')
            level = user.get('riskLevel', 'low').upper()
            state = user.get('riskState', 'none')
            
            # Retrieve forensic detail from the riskDetail enumeration
            detail = user.get('riskDetail', 'none')
            
            # Interpret 'none' values as pending investigative status
            reason = "Awaiting Investigation" if detail == "none" else detail
            
            print(f"{name:<20} | {level:<10} | {state:<12} | {reason}")
            
    except Exception as e:
        print(f"❌ Critical Error: Unable to fetch risk data. {e}")

if __name__ == "__main__":
    get_risk_report()