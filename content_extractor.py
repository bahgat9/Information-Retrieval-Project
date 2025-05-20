
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import random


class BookingScraper:
    def __init__(self):
        try:
            from fake_useragent import UserAgent
            ua = UserAgent()
            user_agent = ua.random
        except:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

        self.headers = {
            'User-Agent': user_agent,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/'
        }

    def scrape_search_results(self, query, pages=1):
        base_url = "https://www.booking.com/searchresults.en-us.html"
        all_hotels = []

        for page in range(pages):
            params = {
                'ss': query,
                'offset': page * 25,
                'checkin': '2025-12-01',
                'checkout': '2026-12-02',
                'group_adults': 1
            }

            try:
                response = requests.get(base_url, params=params, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'lxml')
                with open("debug_html.html", "w", encoding="utf-8") as f:
                    f.write(soup.prettify())
                hotels = soup.find_all('div', {'data-testid': 'property-card'})

                for hotel in hotels:
                    try:
                        data = {
                            'name': hotel.find('div', {'data-testid': 'title'}).text.strip(),
                            'price': hotel.find('span', {'data-testid': 'price-and-discounted-price'}).text.strip(),
                            'score': hotel.find('div', {'data-testid': 'review-score'}).text.strip(),
                            'location': hotel.find('span', {'data-testid': 'address'}).text.strip()
                        }
                        all_hotels.append(data)
                    except AttributeError:
                        continue

                time.sleep(random.uniform(3, 7))

            except Exception as e:
                print(f"Error: {str(e)[:100]}")
                break

        return pd.DataFrame(all_hotels)
