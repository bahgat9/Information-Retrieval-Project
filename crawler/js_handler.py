from playwright.sync_api import sync_playwright
import pandas as pd
from urllib.parse import urlencode
import time
import random


class JSScraper:
    def __init__(self, headless=True, slow_mo=100):
        self.headless = headless
        self.slow_mo = slow_mo
        self.base_url = "https://www.booking.com/searchresults.html"

    def build_search_url(self, destination, checkin, checkout, adults=2, children=0, rooms=1):
        params = {
            'ss': destination,
            'checkin': checkin,
            'checkout': checkout,
            'group_adults': adults,
            'group_children': children,
            'no_rooms': rooms,
            'sb_travel_purpose': 'leisure'
        }
        return f"{self.base_url}?{urlencode(params)}"

    # Update the scrape_hotels method in JSScraper class (js_handler.py)
    def scrape_hotels(self, destination, checkin, checkout, max_results=20, adults=2, children=0, rooms=1):
        url = self.build_search_url(destination, checkin, checkout, adults, children, rooms)
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
            context = browser.new_context()
            page = context.new_page()

            try:
                # Set headers and load search page
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9'
                })

                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                time.sleep(random.uniform(2, 5))

                # Handle cookies popup if it appears
                try:
                    page.click('button#onetrust-accept-btn-handler', timeout=5000)
                    time.sleep(1)
                except:
                    pass

                # Wait for results to load
                page.wait_for_selector('div[data-testid="property-card"]', timeout=30000)

                # Get all hotel elements
                hotel_elements = page.query_selector_all('div[data-testid="property-card"]')
                if not hotel_elements:
                    print("No hotels found on the search results page")
                    return pd.DataFrame()

                for i, hotel in enumerate(hotel_elements[:max_results]):
                    try:
                        # Get basic info from search card
                        name = hotel.query_selector('div[data-testid="title"]').inner_text()
                        price_elem = hotel.query_selector('span[data-testid="price-and-discounted-price"]')
                        price = price_elem.inner_text() if price_elem else "N/A"

                        score_elem = hotel.query_selector('div[data-testid="review-score"]')
                        score = score_elem.inner_text() if score_elem else "N/A"

                        location_elem = hotel.query_selector('span[data-testid="address"]')
                        location = location_elem.inner_text() if location_elem else "N/A"

                        distance_elem = hotel.query_selector('span[data-testid="distance"]')
                        distance = distance_elem.inner_text() if distance_elem else "N/A"

                        # Get hotel URL
                        hotel_url = page.evaluate('(element) => element.querySelector("a").href', hotel)

                        # Open new tab for hotel details
                        hotel_page = context.new_page()
                        hotel_page.goto(hotel_url, timeout=60000, wait_until="domcontentloaded")
                        time.sleep(3)  # Increased wait time for page to fully load

                        # COMBINED FACILITIES SCRAPING APPROACH
                        facilities = []

                        # METHOD 1: Try property highlights (original structure)
                        try:
                            hotel_page.wait_for_selector('div[data-testid="property-highlights"]', timeout=3000)
                            highlight_items = hotel_page.query_selector_all('li[role="listitem"].c5ae8a7f67')
                            for item in highlight_items:
                                text_element = item.query_selector('div.b99b6ef58f.b2b0196c65')
                                if text_element:
                                    facility_text = text_element.inner_text().strip()
                                    if facility_text:
                                        facilities.append(facility_text)
                        except Exception as e:
                            print(f"Property highlights method failed for {name}: {str(e)}")

                        # METHOD 2: Try popular facilities (new structure)
                        if not facilities:
                            try:
                                hotel_page.wait_for_selector(
                                    'div[data-testid="property-most-popular-facilities-wrapper"]', timeout=3000)
                                popular_items = hotel_page.query_selector_all('li.b0bf4dc58f.b2f588b43c')
                                for item in popular_items:
                                    # Try both possible text element locations
                                    text_element = item.query_selector('span.f6b6d2a959') or item.query_selector(
                                        'div.b99b6ef58f')
                                    if text_element:
                                        facility_text = text_element.inner_text().strip()
                                        if facility_text:
                                            facilities.append(facility_text)
                            except Exception as e:
                                print(f"Popular facilities method failed for {name}: {str(e)}")

                        # METHOD 3: Fallback to general facility search
                        if not facilities:
                            try:
                                general_items = hotel_page.query_selector_all('[data-testid="facility-icon"]')
                                for item in general_items:
                                    parent = item.query_selector('xpath=./ancestor::li[1]')
                                    if parent:
                                        text_element = parent.query_selector('div.b99b6ef58f')
                                        if text_element:
                                            facility_text = text_element.inner_text().strip()
                                            if facility_text:
                                                facilities.append(facility_text)
                            except Exception as e:
                                print(f"General facilities method failed for {name}: {str(e)}")
                                facilities = ["Facilities not found"]

                        # Clean and deduplicate
                        seen = set()
                        facilities = [x for x in facilities if x and not (x in seen or seen.add(x))]

                        # Close hotel page tab
                        hotel_page.close()

                        # Build results dictionary
                        results.append({
                            'name': name.strip(),
                            'price': price.strip(),
                            'score': score.strip(),
                            'location': location.strip(),
                            'distance_from_center': distance.strip(),
                            'facilities': ', '.join(facilities) if facilities else "No facilities listed",
                            'url': hotel_url
                        })

                    except Exception as e:
                        print(f"Error processing hotel {i + 1}: {str(e)}")
                        continue

            except Exception as e:
                print(f"Playwright scraping failed: {str(e)}")
            finally:
                context.close()
                browser.close()

        # Create DataFrame with proper data types
        df = pd.DataFrame(results)
        if not df.empty:
            df['price_numeric'] = df['price'].str.replace(r'[^\d.]', '', regex=True).astype(float)
            df['score_clean'] = df['score'].str.extract(r'(\d+\.\d+)')[0].astype(float)

        return df