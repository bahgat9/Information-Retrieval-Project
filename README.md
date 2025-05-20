# Web Crawler & Dashboard – Booking.com (Smart Hotel Listings Crawler)

## Overview
This project is a smart web crawler and dashboard tool that extracts hotel listings from Booking.com using Playwright.  
It supports dynamic JavaScript content and allows the user to input a destination, check-in/check-out dates, and desired number of results.  
The data is displayed through a user-friendly dashboard with filters and CSV export options.

## Features
- Checks crawl permission via `robots.txt`
- Accepts user input (city, dates, number of results)
- Scrapes hotel name, price, rating score, and location
- Displays data in a live dashboard (Streamlit)
- Filter by price and rating using sliders
- Download visible (filtered) results to a CSV file

## Technologies Used
- Python 3.11
- Playwright (JavaScript rendering + scraping)
- Pandas & NumPy (data handling)
- Streamlit (dashboard and interactivity)
- VS Code (development environment)

## Project Structure
```
PythonProject1/
 crawler/
  - js_handler.py          
  - content_extractor.py  
  - robots_analyzer.py    
 dashboard/
  - app.py                
 run.py                     
 requirements.txt
 hotels_data.csv          
```

## How to Run

1. Install requirements:
   ```
   pip install -r requirements.txt
   python -m playwright install
   ```

2. Run the application:
   ```
   python run.py
   ```
   - You’ll be asked to enter:
     - Destination (e.g. London)
     - Check-in and Check-out dates
     - Number of results
   - If left blank, the default will be:
     - Check-in: Today
     - Check-out: 7 days later
     - Max results: 20

3. After scraping finishes, the dashboard will open automatically in your browser.

## Output
- Interactive dashboard (Streamlit):
  - Table of results
  - Sliders to filter by price and rating
  - Download button to export filtered results
- `hotels_data.csv`: Contains all collected hotel information

## Team Contribution
 Member 1 -> Analyzed robots.txt and crawlability 
 Member 2 -> Designed data extraction logic 
 Member 3 -> Implemented JS scraping using Playwright 
 Member 4 -> Built the interactive dashboard 
 Member 5 -> Wrote documentation and organized delivery 

## License
This project was created for academic purposes only.