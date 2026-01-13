"""
Entra ID Auth Auditor: MFA Compliance Reporting Tool
Description: This script programmatically audits the security posture of tenant identities 
             by verifying the registration status of the Microsoft Authenticator app.
Engineer: Ejike Etolue (Jan 2026)
SC-300 Objective: Manage and Monitor User Authentication Methods
"""

import requests
from azure.identity import ClientSecretCredential
import config  # Secured environment variables (Tenant ID, Client ID, Secret)

# --- 🔐 IDENTITY & ACCESS MANAGEMENT (IAM) LAYER ---
# We utilize a Service Principal (App Registration) for non-interactive, 
# service-to-service authentication, following the Principle of Least Privilege.
credential = ClientSecretCredential(
    tenant_id=config.TENANT_ID,
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET
)

# Requesting an OAuth 2.0 Bearer Token specifically for the Microsoft Graph API scope.
token = credential.get_token("https://graph.microsoft.com/.default")
headers = {'Authorization': f'Bearer {token.token}'}

def get_mfa_report():
    """
    Main Logic: Orchestrates the transition from Identity Creation to Identity Governance.
    Fetches all tenant identities and evaluates their specific MFA registration states.
    """
    print("\n--- 🛡️ GENERATING SECURITY COMPLIANCE REPORT ---")
    
    # 1. ORCHESTRATION: Retrieve all user objects within the Entra ID tenant.
    users_url = "https://graph.microsoft.com/v1.0/users"
    try:
        users_response = requests.get(users_url, headers=headers)
        users_response.raise_for_status()  # Ensures the script halts if the API is unreachable
        users = users_response.json().get('value', [])
    except Exception as e:
        print(f"❌ Critical API Error: Unable to fetch user directory. Detail: {e}")
        return

    # 2. AUDIT LOOP: Programmatically interrogate each identity for registered auth methods.
    for user in users:
        u_name = user.get('displayName')
        u_id = user.get('id')
        
        # We target the 'authentication/methods' endpoint to evaluate security strength.
        auth_url = f"https://graph.microsoft.com/v1.0/users/{u_id}/authentication/methods"
        
        try:
            # Execute GET request to retrieve JSON list of the user's registered MFA methods.
            auth_response = requests.get(auth_url, headers=headers)
            auth_response.raise_for_status()
            methods = auth_response.json().get('value', [])
            
            # EVALUATION LOGIC: Check for 'microsoftAuthenticator' within the OData types.
            # This identifies if the user has moved beyond insecure legacy authentication.
            has_app = any("microsoftAuthenticator" in str(m.get('@odata.type')) for m in methods)
            
            if has_app:
                print(f"✅ {u_name.ljust(20)}: Authenticator App Registered")
            else:
                print(f"❌ {u_name.ljust(20)}: NON-COMPLIANT (MFA Gap Detected)")
                
        except requests.exceptions.HTTPError as err:
            # DEFENSIVE CODING: Handles restricted accounts or edge cases (e.g., 403 Forbidden).
            print(f"⚠️  {u_name.ljust(20)}: [SKIP] Access Denied or No Methods (HTTP {err.response.status_code})")
        except Exception as e:
            # General exception handling to ensure script resilience during high-volume audits.
            print(f"⚠️  {u_name.ljust(20)}: [SYSTEM ERROR] {e}")

if __name__ == "__main__":
    get_mfa_report()