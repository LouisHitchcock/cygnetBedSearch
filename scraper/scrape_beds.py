from playwright.sync_api import sync_playwright
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.api_client import send_to_api

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


def main():
    data = get_bed_availability()
    if data:
        send_to_api(data)
        print(f"Sent {len(data)} rows to the API")
    else:
        print("No data scraped.")


if __name__ == "__main__":
    main()
