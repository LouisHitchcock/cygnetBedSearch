import requests
from bs4 import BeautifulSoup
import csv
import os

# List of URLs to scrape along with their respective purposes
URLS = [
    ("https://www.cygnetgroup.com/professionals/bed-placement-search/?select-service=health-care-services&service=84&social_care_service=&gender=all", "Rehab"),
    ("https://www.cygnetgroup.com/professionals/bed-placement-search/?select-service=&service=87&social_care_service=&gender=all", "PDU"),
    ("https://www.cygnetgroup.com/professionals/bed-placement-search/?select-service=&service=81&social_care_service=&gender=all", "Acute/PICU")
]

def get_bed_availability():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    data = []
    
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
                    gender = "Mixed"
                    if gender_element:
                        gender_classes = gender_element.find_all('span')
                        if any('icon--male' in gender['class'] for gender in gender_classes):
                            gender = "Male"
                        elif any('icon--female' in gender['class'] for gender in gender_classes):
                            gender = "Female"

                    data.append([ward_name, ward_name.split()[-1], gender, purpose, bed_count, "Last Updated Date Here"])
        else:
            print(f"Failed to retrieve data from {url}: {response.status_code}")

    return data

def save_to_csv(data):
    with open('bed_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Location', 'Gender', 'Purpose', 'Beds', 'Last Updated'])
        writer.writerows(data)

def main():
    # Get current bed availability data
    data = get_bed_availability()
    
    # Save current data to CSV
    save_to_csv(data)

if __name__ == "__main__":
    main()
    print("Data has been written to bed_data.csv")
