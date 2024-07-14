import requests
import pandas as pd

# Hunter.io API Key
HUNTER_API_KEY = '4d4f9d12a263955ee3bca0bd6b2851a076e6ec8a'

def find_email_hunter(domain, first_name, last_name):
    url = f'https://api.hunter.io/v2/email-finder?domain={domain}&first_name={first_name}&last_name={last_name}&api_key={HUNTER_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"Email found for {first_name} {last_name} at {domain}: {data.get('data', {}).get('email', None)}")
        return data
    except requests.RequestException as e:
        print(f"Error finding email for {first_name} {last_name} at {domain}: {e}")
        return {}

def verify_email_hunter(email):
    url = f'https://api.hunter.io/v2/email-verifier?email={email}&api_key={HUNTER_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"Verification data for {email}: {data.get('data', {})}")
        return data
    except requests.RequestException as e:
        print(f"Error verifying email {email}: {e}")
        return {}

# Function to profile an email
def profile_email(domain, first_name, last_name):
    profile = {'domain': domain, 'first_name': first_name, 'last_name': last_name}
    
    # Find email with Hunter.io
    hunter_find_data = find_email_hunter(domain, first_name, last_name)
    profile['found_email'] = hunter_find_data.get('data', {}).get('email', None)
    
    if profile['found_email']:
        # Verify email with Hunter.io
        hunter_verify_data = verify_email_hunter(profile['found_email'])
        profile['email_verification'] = hunter_verify_data.get('data', {})
    else:
        profile['email_verification'] = {}
    
    return profile

# Function to profile a list of people
def profile_people(people):
    profiles = []
    for person in people:
        profile = profile_email(person['domain'], person['first_name'], person['last_name'])
        profiles.append(profile)
    return profiles

# Function to load manual data corrections
def load_manual_data(file_path):
    try:
        manual_data = pd.read_excel(file_path)
        return manual_data
    except Exception as e:
        print(f"Error loading manual data from {file_path}: {e}")
        return pd.DataFrame()

# Main function
if __name__ == '__main__':
    # Define list of people to profile
    people = [
        {'domain': 'stripe.com', 'first_name': 'Patrick', 'last_name': 'Collison'},
        {'domain': 'stripe.com', 'first_name': 'John', 'last_name': 'Doe'}
    ]

    # Profile people
    profiles = profile_people(people)
    print("Profiles collected:", profiles)

    # Convert profiles to DataFrame
    df_automated = pd.DataFrame(profiles)
    print("Automated profile DataFrame:\n", df_automated)

    # Load manual data corrections (ensure this file exists for the test to work)
    manual_data_file = 'manual_profile_template.xlsx'
    df_manual = load_manual_data(manual_data_file)
    print("Manual profile DataFrame:\n", df_manual)

    # Merge automated data with manual data
    df_final = df_manual.combine_first(df_automated)
    print("Final merged DataFrame:\n", df_final)

    # Save final profiles to CSV
    output_file = 'final_email_profiles.csv'
    df_final.to_csv(output_file, index=False)
    print(f"Final email profiles saved to '{output_file}'")
