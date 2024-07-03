import requests
from bs4 import BeautifulSoup
import json
import os

def get_bed_availability():
    url = "https://www.cygnetgroup.com/professionals/bed-placement-search/?select-service=health-care-services&service=84&social_care_service="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        bed_results = soup.find_all('article', class_='result')
        
        male_wards = {}
        female_wards = {}
        
        for result in bed_results:
            ward_name = result.find('h1', class_='result__heading').text.strip()
            bed_count_element = result.find('div', class_='result__quantity-heading')
            gender_element = result.find('span', class_='result__icons')

            if bed_count_element:
                bed_count = int(bed_count_element.text.strip().split()[0])
                if bed_count > 0:
                    if gender_element:
                        gender_classes = gender_element.find_all('span')
                        if any('icon--male' in gender['class'] for gender in gender_classes):
                            male_wards[ward_name] = bed_count
                        elif any('icon--female' in gender['class'] for gender in gender_classes):
                            female_wards[ward_name] = bed_count

        return male_wards, female_wards
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return {}, {}

def load_previous_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

def save_current_data(file_path, male_wards, female_wards):
    with open(file_path, 'w') as file:
        json.dump({'male_wards': male_wards, 'female_wards': female_wards}, file, indent=4)

def compare_data(old_data, new_data):
    differences = {"added": {}, "removed": {}, "updated": {}}
    for ward, beds in new_data.items():
        if ward not in old_data:
            differences["added"][ward] = beds
        elif old_data[ward] != beds:
            differences["updated"][ward] = {"old": old_data[ward], "new": beds}

    for ward in old_data:
        if ward not in new_data:
            differences["removed"][ward] = old_data[ward]

    return differences

def print_differences(differences, ward_type):
    print(f"{ward_type} Ward Differences:")
    if differences["added"]:
        print("Added:")
        for ward, beds in differences["added"].items():
            print(f"  - {ward}: {beds} beds")
    if differences["removed"]:
        print("Removed:")
        for ward, beds in differences["removed"].items():
            print(f"  - {ward}: {beds} beds")
    if differences["updated"]:
        print("Updated:")
        for ward, change in differences["updated"].items():
            print(f"  - {ward}: {change['old']} -> {change['new']} beds")
    if not any(differences.values()):
        print("  No changes")

def print_current_beds(male_wards, female_wards):
    print("Current Bed Availability:")
    print("\nMale Wards:")
    for ward, beds in male_wards.items():
        print(f"  - {ward}: {beds} beds")
    
    print("\nFemale Wards:")
    for ward, beds in female_wards.items():
        print(f"  - {ward}: {beds} beds")

def main():
    data_file = 'bed_availability.json'
    
    # Get current bed availability data
    current_male_wards, current_female_wards = get_bed_availability()
    
    # Print current bed availability
    print_current_beds(current_male_wards, current_female_wards)
    
    # Load previous data
    previous_data = load_previous_data(data_file)
    
    # Compare previous and current data
    male_differences = compare_data(previous_data.get('male_wards', {}), current_male_wards)
    female_differences = compare_data(previous_data.get('female_wards', {}), current_female_wards)
    
    # Print differences
    print("\nChanges Since Last Check:")
    print_differences(male_differences, "Male")
    print_differences(female_differences, "Female")
    
    # Save current data
    save_current_data(data_file, current_male_wards, current_female_wards)

if __name__ == "__main__":
    main()
