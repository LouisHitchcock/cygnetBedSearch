import requests
from bs4 import BeautifulSoup
import json
import os
import tkinter as tk

# Define the path for saving favorites
FAVORITES_FILE = 'favorites.json'

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

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r') as file:
            return json.load(file)
    return []

def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w') as file:
        json.dump(favorites, file, indent=4)

def toggle_favorite(label, ward_name, favorites):
    if ward_name in favorites:
        favorites.remove(ward_name)
        label.config(fg="black")
    else:
        favorites.append(ward_name)
        label.config(fg="red")
    save_favorites(favorites)

def update_ui(current_male_wards, current_female_wards, male_differences, female_differences, favorites):
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Bed Availability", font=("Arial", 12, "bold")).grid(row=0, columnspan=4, pady=10)

    tk.Label(root, text="Male Wards", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=10)
    tk.Label(root, text="Female Wards", font=("Arial", 10, "bold")).grid(row=1, column=2, padx=10)

    male_row = 2
    for ward, beds in current_male_wards.items():
        label = tk.Label(root, text=f"{ward}: {beds} beds", fg="red" if ward in favorites else "black")
        label.grid(row=male_row, column=0, padx=10, sticky='w')
        label.bind("<Button-1>", lambda e, lbl=label, wn=ward: toggle_favorite(lbl, wn, favorites))
        male_row += 1

    female_row = 2
    for ward, beds in current_female_wards.items():
        label = tk.Label(root, text=f"{ward}: {beds} beds", fg="red" if ward in favorites else "black")
        label.grid(row=female_row, column=2, padx=10, sticky='w')
        label.bind("<Button-1>", lambda e, lbl=label, wn=ward: toggle_favorite(lbl, wn, favorites))
        female_row += 1

    if any(male_differences.values()) or any(female_differences.values()):
        tk.Label(root, text="Changes", font=("Arial", 12, "bold")).grid(row=max(male_row, female_row), columnspan=4, pady=10)
        changes_row = max(male_row, female_row) + 1
        tk.Label(root, text="Male Wards", font=("Arial", 10, "bold")).grid(row=changes_row, column=0, padx=10)
        tk.Label(root, text="Female Wards", font=("Arial", 10, "bold")).grid(row=changes_row, column=2, padx=10)
        changes_row += 1
        
        for ward, beds in male_differences["added"].items():
            tk.Label(root, text=f"Added: {ward}: {beds} beds").grid(row=changes_row, column=0, padx=10, sticky='w')
            changes_row += 1
        for ward, beds in male_differences["removed"].items():
            tk.Label(root, text=f"Removed: {ward}: {beds} beds").grid(row=changes_row, column=0, padx=10, sticky='w')
            changes_row += 1
        for ward, change in male_differences["updated"].items():
            tk.Label(root, text=f"Updated: {ward}: {change['old']} -> {change['new']} beds").grid(row=changes_row, column=0, padx=10, sticky='w')
            changes_row += 1

        changes_row = max(male_row, female_row) + 1
        for ward, beds in female_differences["added"].items():
            tk.Label(root, text=f"Added: {ward}: {beds} beds").grid(row=changes_row, column=2, padx=10, sticky='w')
            changes_row += 1
        for ward, beds in female_differences["removed"].items():
            tk.Label(root, text=f"Removed: {ward}: {beds} beds").grid(row=changes_row, column=2, padx=10, sticky='w')
            changes_row += 1
        for ward, change in female_differences["updated"].items():
            tk.Label(root, text=f"Updated: {ward}: {change['old']} -> {change['new']} beds").grid(row=changes_row, column=2, padx=10, sticky='w')
            changes_row += 1

def main():
    data_file = 'bed_availability.json'
    
    # Get current bed availability data
    current_male_wards, current_female_wards = get_bed_availability()
    
    # Load previous data
    previous_data = load_previous_data(data_file)
    
    # Compare previous and current data
    male_differences = compare_data(previous_data.get('male_wards', {}), current_male_wards)
    female_differences = compare_data(previous_data.get('female_wards', {}), current_female_wards)
    
    # Load favorites
    favorites = load_favorites()
    
    # Update the UI with the current data and differences
    update_ui(current_male_wards, current_female_wards, male_differences, female_differences, favorites)
    
    # Save current data
    save_current_data(data_file, current_male_wards, current_female_wards)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bed Availability Checker")
    root.geometry("600x600")
    main()
    root.mainloop()
