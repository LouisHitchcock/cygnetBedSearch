import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

URLS = [
    ("https://www.cygnetgroup.com/professionals/bed-placement-search/?select-service=health-care-services&service=84&social_care_service=&gender=all", "Rehab"),
    ("https://www.cygnetgroup.com/professionals/bed-placement-search/?select-service=&service=87&social_care_service=&gender=all", "PDU"),
    ("https://www.cygnetgroup.com/professionals/bed-placement-search/?select-service=&service=81&social_care_service=&gender=all", "Acute/PICU")
]

def scrape_bed_data():
    data = []
    for url, purpose in URLS:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        wards = soup.find_all('div', class_='ward-info')
        for ward in wards:
            name = ward.find('h3').text.strip()
            location = ward.find('p', class_='location').text.strip()
            gender = ward.find('p', class_='gender').text.strip()
            beds = int(ward.find('p', class_='beds').text.split()[0])
            data.append({
                'name': name,
                'location': location,
                'gender': gender,
                'purpose': purpose,
                'beds': beds,
                'timestamp': datetime.datetime.now()
            })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = scrape_bed_data()
    df.to_csv('bed_data.csv', index=False)
