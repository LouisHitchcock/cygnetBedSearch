import pandas as pd
import datetime

# Provided ward data
WARD_DATA = {
    "male_wards": {
        "Cygnet Storthfield House": 4,
        "Cygnet Hospital Derby": 4,
        "Cygnet Hospital Kewstoke": 4,
        "Cygnet St Augustine’s": 4,
        "Cygnet Delfryn House": 4,
        "Cygnet Hospital Colchester": 3,
        "Cygnet Fountains": 3,
        "Cygnet Oaks": 2,
        "Gledholt Mews and Coach House": 2,
        "Cygnet Hospital Maidstone": 2,
        "1 Vincent Court": 2,
        "15 The Sycamores": 2,
        "12 Woodcross Street": 1,
        "20A and 20B Turls Hill Road": 1,
        "Cygnet Lodge Woking": 1
    },
    "female_wards": {
        "Cygnet Lodge Kenton": 3,
        "Cygnet Aspen House": 3,
        "Ty Alarch": 2,
        "Cygnet St Teilo House": 2,
        "Cygnet Delfryn Lodge": 2
    }
}

def format_ward_data(ward_data):
    data = []
    for gender, wards in ward_data.items():
        for ward_name, beds in wards.items():
            data.append({
                'name': ward_name,
                'location': "Unknown",  # Assuming location is unknown
                'gender': "Male" if gender == "male_wards" else "Female",
                'purpose': "Unknown",  # Assuming purpose is unknown
                'beds': beds,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = format_ward_data(WARD_DATA)
    df.to_csv('provided_ward_data.csv', index=False)
