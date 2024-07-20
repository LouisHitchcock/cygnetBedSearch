# Cygnet Bed Tracker

[![Build Status](https://github.com/louishitchcock/cygnetBedSearch/actions/workflows/scrape_beds.yml/badge.svg)](https://github.com/louishitchcock/cygnetBedSearch/actions)

This project contains a web scraper that collects bed availability data from Cygnet Health Care's website and displays it on a web page. The scraper runs every 6 hours using GitHub Actions and appends the latest data to a CSV file. The data is then visualized on a web page using Chart.js.

## Features

- Scrapes bed availability data from specified URLs.
- Appends new data to an existing CSV file without overwriting previous data.
- Visualizes the data on a web page using Chart.js.
- Automated data scraping every 6 hours using GitHub Actions.

## Project Structure

- `scrape_beds.py`: Python script that scrapes the bed availability data and saves it to `bed_data.csv`.
- `bed_data.csv`: CSV file that stores the scraped data.
- `index.html`: HTML file that visualizes the bed availability data.
- `style.css`: CSS file for styling the web page.
- `.github/workflows/scrape_beds.yml`: GitHub Actions workflow file that schedules and runs the scraper every 6 hours.

## How to Use

1. **Clone the Repository**: 
    ```sh
    git clone https://github.com/louishitchcock/cygnetBedSearch.git
    cd cygnetBedSearch
    ```

2. **Set Up Python Environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. **Run the Scraper Locally**:
    ```sh
    python scrape_beds.py
    ```

4. **View the Data**:
    Open `index.html` in your web browser to view the latest bed availability data.

## Deployment

The project is deployed on GitHub Pages. You can view the latest bed availability data here: [Cygnet Bed Tracker](https://louishitchcock.github.io/cygnetBedSearch/)

## Automated Workflow

The scraper runs every 6 hours using GitHub Actions. The workflow file `.github/workflows/scrape_beds.yml` defines the schedule and steps for running the scraper, committing new data, and pushing it to the repository.

![Build Status](https://github.com/louishitchcock/cygnetBedSearch/actions/workflows/scrape_beds.yml/badge.svg)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
