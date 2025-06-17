import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os

# List of URLs to scrape along with their respective purposes
URLS = [
    ("https://www.cygnetgroup.com/professionals/bed-placement-search/health-care-bed-availability/?service=84&social_care_service=&gender=all", "Rehab"),
    ("https://www.cygnetgroup.com/professionals/bed-placement-search/health-care-bed-availability/?service=87&social_care_service=&gender=all", "PDU"),
    ("https://www.cygnetgroup.com/professionals/bed-placement-search/health-care-bed-availability/?service=81&social_care_service=&gender=all", "Acute/PICU")
]

from playwright.sync_api import sync_playwright
from datetime import datetime

def get_bed_availability():
    data = []
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    URLS = [
        ("https://www.cygnetgroup.com/professionals/bed-placement-search/health-care-bed-availability/?service=84&social_care_service=&gender=all", "Rehab"),
        ("https://www.cygnetgroup.com/professionals/bed-placement-search/health-care-bed-availability/?service=87&social_care_service=&gender=all", "PDU"),
        ("https://www.cygnetgroup.com/professionals/bed-placement-search/health-care-bed-availability/?service=81&social_care_service=&gender=all", "Acute/PICU")
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for url, purpose in URLS:
            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector('article.result', timeout=10000)

                articles = page.query_selector_all('article.result')
                for article in articles:
                    ward = article.query_selector('h1.result__heading')
                    beds = article.query_selector('div.result__quantity-heading')
                    gender_icon = article.query_selector('span.result__icons')

                    if ward and beds:
                        name = ward.inner_text().strip()
                        bed_count = int(beds.inner_text().strip().split()[0])
                        gender = "Mixed"
                        if gender_icon:
                            icon_classes = gender_icon.inner_html()
                            if 'icon--male' in icon_classes:
                                gender = "Male"
                            elif 'icon--female' in icon_classes:
                                gender = "Female"

                        data.append([name, gender, bed_count, purpose, date, time])
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")

        browser.close()
    return data


def save_to_csv(data):
    file_exists = os.path.isfile('.//bed_data.csv')
    with open('./bed_data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Name', 'Sex', 'Number of Beds', 'Purpose', 'Date', 'Time'])
        writer.writerows(data)

def main():
    # Get current bed availability data
    data = get_bed_availability()
    
    # Save current data to CSV
    save_to_csv(data)

if __name__ == "__main__":
    main()
    print("Data has been added to ./scraper/bed_data.csv")
