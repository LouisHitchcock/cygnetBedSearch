import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Replace these with your own credentials and spreadsheet ID
CLIENT_SECRET_FILE = './client_secret_1058605601312-89fgoocsjd8mmdqq9vr5q1djt3o61d6f.apps.googleusercontent.com.json'
SPREADSHEET_ID = '1j1vRt47CWTPuQy7xxUBSQeN4GJrtfLaBFc6RTRvUne4'
RANGE_NAME = 'Sheet1!A2:D'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_bed_availability():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    URLS = [
        ("https://www.cygnetgroup.com/professionals/bed-placement-search/?select-service=health-care-services&service=84&social_care_service=&gender=all", "Rehab"),
        ("https://www.cygnetgroup.com/professionals/bed-placement-search/?select-service=&service=87&social_care_service=&gender=all", "PDU"),
        ("https://www.cygnetgroup.com/professionals/bed-placement-search/?select-service=&service=81&social_care_service=&gender=all", "Acute/PICU")
    ]
    
    male_wards = {}
    female_wards = {}
    
    for url, purpose in URLS:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            bed_results = soup.find_all('article', class_='result')
            
            for result in bed_results:
                ward_name_element = result.find('h1', class_='result__heading')
                bed_count_element = result.find('div', class_='result__quantity-heading')
                gender_element = result.find('span', class_='result__icons')

                if ward_name_element and bed_count_element:
                    ward_name = ward_name_element.text.strip()
                    bed_count = int(bed_count_element.text.strip().split()[0])

                    if bed_count > 0:
                        ward_info = {
                            'beds': bed_count,
                            'purpose': purpose
                        }
                        if gender_element:
                            gender_classes = gender_element.find_all('span')
                            if any('icon--male' in gender['class'] for gender in gender_classes):
                                male_wards[ward_name] = ward_info
                            elif any('icon--female' in gender['class'] for gender in gender_classes):
                                female_wards[ward_name] = ward_info
        else:
            print(f"Failed to retrieve data from {url}: {response.status_code}")

    return male_wards, female_wards

def save_data(male_wards, female_wards):
    data = {
        'male_wards': male_wards,
        'female_wards': female_wards
    }
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

def log_changes(male_wards, female_wards):
    if not os.path.exists('change_log.json') or os.path.getsize('change_log.json') == 0:
        change_log = []
    else:
        with open('change_log.json', 'r') as f:
            change_log = json.load(f)
    
    total_changes = len(male_wards) + len(female_wards)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    change_log.append({'timestamp': timestamp, 'changes': total_changes})
    
    with open('change_log.json', 'w') as f:
        json.dump(change_log, f, indent=4)

def update_google_sheet(male_wards, female_wards):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    values = []
    for ward, info in male_wards.items():
        values.append([ward, info['beds'], info['purpose'], 'Male'])
    for ward, info in female_wards.items():
        values.append([ward, info['beds'], info['purpose'], 'Female'])

    body = {
        'values': values
    }
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f"{result.get('updatedCells')} cells updated.")

def main():
    male_wards, female_wards = get_bed_availability()
    save_data(male_wards, female_wards)
    log_changes(male_wards, female_wards)
    update_google_sheet(male_wards, female_wards)

if __name__ == "__main__":
    main()
