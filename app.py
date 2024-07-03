import requests
from bs4 import BeautifulSoup
import json
import os
import streamlit as st

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
        st.error(f"Failed to retrieve data: {response.status_code}")
        return {}, {}

def load_previous_data(file_path):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
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
    if os.path.exists(FAVORITES_FILE) and os.path.getsize(FAVORITES_FILE) > 0:
        with open(FAVORITES_FILE, 'r') as file:
            return json.load(file)
    return []

def save_favorites(favorites):
    with open(FAVORITES_FILE, 'w') as file:
        json.dump(favorites, file, indent=4)

# Initialize session state for favorites
if 'favorites' not in st.session_state:
    st.session_state.favorites = load_favorites()

def toggle_favorite(ward_name):
    if ward_name in st.session_state.favorites:
        st.session_state.favorites.remove(ward_name)
    else:
        st.session_state.favorites.append(ward_name)
    save_favorites(st.session_state.favorites)
    st.rerun()  # Trigger rerun to update the UI

# Custom CSS for styling
st.markdown("""
    <style>
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid black;
        padding: 8px;
        text-align: center;
    }
    th {
        background-color: #f2f2f2;
    }
    .star {
        cursor: pointer;
        font-size: 20px;
        color: gold;
    }
    .favorite {
        color: red;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    data_file = 'bed_availability.json'
    
    # Get current bed availability data
    current_male_wards, current_female_wards = get_bed_availability()
    
    # Load previous data
    previous_data = load_previous_data(data_file)
    
    # Compare previous and current data
    male_differences = compare_data(previous_data.get('male_wards', {}), current_male_wards)
    female_differences = compare_data(previous_data.get('female_wards', {}), current_female_wards)
    
    st.title("Bed Availability Checker")

    st.subheader("Bed Availability")
    
    male_ward_rows = ""
    for ward, beds in current_male_wards.items():
        star = "★" if ward in st.session_state.favorites else "☆"
        favorite_class = "favorite" if ward in st.session_state.favorites else ""
        male_ward_rows += f"""
        <tr>
            <td class="ward-name {favorite_class}">{ward}</td>
            <td>{beds}</td>
            <td><span class="star" onclick="window.location.href='?fav_ward={ward}'">{star}</span></td>
        </tr>
        """
    
    female_ward_rows = ""
    for ward, beds in current_female_wards.items():
        star = "★" if ward in st.session_state.favorites else "☆"
        favorite_class = "favorite" if ward in st.session_state.favorites else ""
        female_ward_rows += f"""
        <tr>
            <td class="ward-name {favorite_class}">{ward}</td>
            <td>{beds}</td>
            <td><span class="star" onclick="window.location.href='?fav_ward={ward}'">{star}</span></td>
        </tr>
        """
    
    table_html = f"""
    <table>
        <tr>
            <th>Male Wards</th>
            <th></th>
            <th></th>
            <th>Female Wards</th>
            <th></th>
            <th></th>
        </tr>
        <tr>
            <th>Ward Name</th>
            <th>Number of Beds</th>
            <th>Favorite</th>
            <th>Ward Name</th>
            <th>Number of Beds</th>
            <th>Favorite</th>
        </tr>
        <tr>
            <td colspan="3">
                <table>
                    {male_ward_rows}
                </table>
            </td>
            <td colspan="3">
                <table>
                    {female_ward_rows}
                </table>
            </td>
        </tr>
    </table>
    """

    st.markdown(table_html, unsafe_allow_html=True)

    if any(male_differences.values()) or any(female_differences.values()):
        st.subheader("Changes")
        st.text("Male Wards")
        for ward, beds in male_differences["added"].items():
            st.text(f"Added: {ward}: {beds} beds")
        for ward, beds in male_differences["removed"].items():
            st.text(f"Removed: {ward}: {beds} beds")
        for ward, change in male_differences["updated"].items():
            st.text(f"Updated: {ward}: {change['old']} -> {change['new']} beds")

        st.text("Female Wards")
        for ward, beds in female_differences["added"].items():
            st.text(f"Added: {ward}: {beds} beds")
        for ward, beds in female_differences["removed"].items():
            st.text(f"Removed: {ward}: {beds} beds")
        for ward, change in female_differences["updated"].items():
            st.text(f"Updated: {ward}: {change['old']} -> {change['new']} beds")

    # Save current data
    save_current_data(data_file, current_male_wards, current_female_wards)

if __name__ == "__main__":
    # Check for query parameter to toggle favorite
    fav_ward = st.experimental_get_query_params().get("fav_ward", [None])[0]
    if fav_ward:
        toggle_favorite(fav_ward)
        st.experimental_set_query_params()  # Clear the query params

    main()
