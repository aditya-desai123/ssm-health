import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from zip_msa_lookup import ZipMSALookup

class SSMHealthLocationsScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with Chrome driver options"""
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        self.driver = None
        self.locations = []
        self.msa_lookup = ZipMSALookup()
    
    def start_driver(self):
        """Start the Chrome WebDriver"""
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.implicitly_wait(10)
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
    
    def wait_for_locations_to_load(self, timeout=20):
        """Wait for location cards to be present on the page"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".card.card-body[data-location]"))
            )
            return True
        except TimeoutException:
            print("Timeout waiting for location cards to load")
            # Try fallback selector
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".card.card-body"))
                )
                return True
            except TimeoutException:
                print("Timeout waiting for any card elements to load")
                return False
    
    def extract_location_data(self, location_element):
        """Extract data from a single location element"""
        location_data = {}
        
        try:
            # Extract location name from h2 element
            try:
                name_element = location_element.find_element(By.CSS_SELECTOR, 'h2.txt-md')
                location_data['name'] = name_element.text.strip()
            except NoSuchElementException:
                location_data['name'] = 'N/A'
            
            # Extract address components
            try:
                addr_div = location_element.find_element(By.CSS_SELECTOR, '.addr')
                
                # Get street address
                street = addr_div.find_element(By.CSS_SELECTOR, '.addr-span-street').text.strip()
                
                # Get city, state, zip
                city = addr_div.find_element(By.CSS_SELECTOR, '.addr-span-city').text.strip()
                state = addr_div.find_element(By.CSS_SELECTOR, '.addr-span-state').text.strip()
                zip_code = addr_div.find_element(By.CSS_SELECTOR, '.addr-span-zip').text.strip()
                
                # Combine into full address
                location_data['address'] = f"{street}, {city}, {state} {zip_code}"
                location_data['street'] = street
                location_data['city'] = city
                location_data['state'] = state
                location_data['zip'] = zip_code
                
            except NoSuchElementException:
                location_data['address'] = 'N/A'
                location_data['street'] = 'N/A'
                location_data['city'] = 'N/A'
                location_data['state'] = 'N/A'
                location_data['zip'] = 'N/A'
            
            # Extract phone number
            try:
                phone_element = location_element.find_element(By.CSS_SELECTOR, 'a.phonenumber')
                location_data['phone'] = phone_element.text.strip()
            except NoSuchElementException:
                location_data['phone'] = 'N/A'
            
            # Extract location type from badges
            try:
                badges_element = location_element.find_element(By.CSS_SELECTOR, '.badges span')
                badge_text = badges_element.text.strip()
                # Extract type after "Type: "
                if badge_text.startswith('Type: '):
                    location_data['type'] = badge_text.replace('Type: ', '')
                else:
                    location_data['type'] = badge_text
            except NoSuchElementException:
                location_data['type'] = 'N/A'
            
            # Extract specialty information
            try:
                specialty_element = location_element.find_element(By.CSS_SELECTOR, '.loc-specialty')
                location_data['specialty'] = specialty_element.text.strip()
            except NoSuchElementException:
                location_data['specialty'] = 'N/A'
            
            # Extract hours
            try:
                hours_element = location_element.find_element(By.CSS_SELECTOR, '.collapsed-days')
                location_data['hours'] = hours_element.text.strip()
            except NoSuchElementException:
                location_data['hours'] = 'N/A'
            
            # Extract distance (if available)
            try:
                distance_elements = location_element.find_elements(By.CSS_SELECTOR, '.mt-025')
                for elem in distance_elements:
                    text = elem.text.strip()
                    if 'miles' in text:
                        location_data['distance'] = text
                        break
                else:
                    location_data['distance'] = 'N/A'
            except NoSuchElementException:
                location_data['distance'] = 'N/A'
            
            # Extract main location link
            try:
                link_element = location_element.find_element(By.CSS_SELECTOR, 'a[href*="/locations/"]')
                location_data['link'] = link_element.get_attribute('href')
            except NoSuchElementException:
                location_data['link'] = 'N/A'
            
            # Extract location ID from data attribute
            try:
                location_data['location_id'] = location_element.get_attribute('data-location')
            except:
                location_data['location_id'] = 'N/A'
            
            # Extract image URL
            try:
                img_element = location_element.find_element(By.CSS_SELECTOR, '.loc-amp-img')
                location_data['image_url'] = img_element.get_attribute('src')
            except NoSuchElementException:
                location_data['image_url'] = 'N/A'
            
            # Extract ZIP code from address for better MSA lookup
            zip_code = None
            if location_data['address'] != 'N/A':
                # Try to extract ZIP from address
                parts = location_data['address'].split(',')
                if len(parts) >= 3:
                    state_zip = parts[2].strip()
                    words = state_zip.split()
                    for word in words:
                        if len(word) == 5 and word.isdigit():
                            zip_code = word
                            break
            
            location_data['zip_code'] = zip_code if zip_code else 'N/A'
            
            # Add MSA information using ZIP code if available
            if zip_code and zip_code != 'N/A':
                msa_data = self.msa_lookup.get_msa_from_zip_api(zip_code)
                location_data['msa'] = msa_data['msa_name']
                location_data['msa_code'] = msa_data['msa_code']
                location_data['msa_source'] = msa_data['source']
            elif location_data['city'] != 'N/A' and location_data['state'] != 'N/A':
                msa_data = self.msa_lookup.get_msa(location_data['city'], location_data['state'])
                location_data['msa'] = msa_data['msa_name']
                location_data['msa_code'] = msa_data['msa_code']
                location_data['msa_source'] = msa_data['source']
            else:
                msa_data = self.msa_lookup.get_msa_from_address(location_data['address'])
                location_data['msa'] = msa_data['msa_name']
                location_data['msa_code'] = msa_data['msa_code']
                location_data['msa_source'] = msa_data['source']
            
        except Exception as e:
            print(f"Error extracting location data: {e}")
            location_data = {
                'name': 'Error extracting data',
                'address': 'N/A',
                'street': 'N/A',
                'city': 'N/A',
                'state': 'N/A',
                'zip': 'N/A',
                'zip_code': 'N/A',
                'phone': 'N/A',
                'type': 'N/A',
                'specialty': 'N/A',
                'hours': 'N/A',
                'distance': 'N/A',
                'link': 'N/A',
                'location_id': 'N/A',
                'image_url': 'N/A',
                'msa': 'Unknown',
                'msa_code': '00000',
                'msa_source': 'Error'
            }
        
        return location_data
    
    def scrape_current_page(self):
        """Scrape all locations from the current page"""
        page_locations = []
        
        # Wait for locations to load
        if not self.wait_for_locations_to_load():
            return page_locations
        
        # Look for the specific SSM Health location cards
        try:
            location_elements = self.driver.find_elements(By.CSS_SELECTOR, ".card.card-body[data-location]")
            print(f"Found {len(location_elements)} location cards")
            
            if not location_elements:
                # Fallback: try just .card.card-body
                location_elements = self.driver.find_elements(By.CSS_SELECTOR, ".card.card-body")
                print(f"Fallback: Found {len(location_elements)} card elements")
            
        except Exception as e:
            print(f"Error finding location elements: {e}")
            return page_locations
        
        for i, element in enumerate(location_elements):
            try:
                location_data = self.extract_location_data(element)
                if location_data['name'] != 'N/A' and location_data['name'] != 'Error extracting data':
                    page_locations.append(location_data)
                    print(f"  {i+1}. {location_data['name']} - {location_data['address']}")
                else:
                    print(f"  {i+1}. Skipped location with no name")
            except Exception as e:
                if "invalid session id" in str(e).lower() or "session deleted" in str(e).lower():
                    print(f"Session error while processing location {i+1}: {e}")
                    # Return what we have so far, the main loop will handle recovery
                    return page_locations
                else:
                    print(f"Error processing location {i+1}: {e}")
                    continue
        
        return page_locations
    
    def find_and_click_next_button(self):
        """Find and click the next page button"""
        # Get current page number
        current_page = 1
        try:
            selected_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.selected.page-link")
            current_page = int(selected_button.get_attribute('data-page'))
        except:
            pass
        
        def safe_click_element(element):
            """Safely click an element with multiple fallback methods"""
            try:
                # Method 1: Scroll to element and click
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(2)
                element.click()
                return True
            except Exception as e1:
                try:
                    # Method 2: Use JavaScript click
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception as e2:
                    try:
                        # Method 3: Scroll to bottom and try again
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)
                        element.click()
                        return True
                    except Exception as e3:
                        print(f"All click methods failed: {e1}, {e2}, {e3}")
                        return False
        
        # If we're on a page that's a multiple of 5 (5, 10, 15, etc.), 
        # we need to click the next arrow button to advance to the next set
        if current_page % 5 == 0:
            try:
                next_arrow_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.page-link.icon.right-arrow")
                if next_arrow_button.is_enabled() and next_arrow_button.is_displayed():
                    if safe_click_element(next_arrow_button):
                        time.sleep(3)  # Wait for page to load
                        return True
            except NoSuchElementException:
                pass
        
        # For pages within the current set (1-5, 6-10, etc.), try to find the next page number button
        try:
            next_page = current_page + 1
            next_button = self.driver.find_element(By.CSS_SELECTOR, f"button.btn.page-link[data-page='{next_page}']")
            
            if next_button.is_enabled() and next_button.is_displayed():
                if safe_click_element(next_button):
                    time.sleep(3)  # Wait for page to load
                    return True
        except NoSuchElementException:
            pass
        
        # If we can't find the next page number button, try the next arrow button as fallback
        try:
            next_arrow_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.page-link.icon.right-arrow")
            if next_arrow_button.is_enabled() and next_arrow_button.is_displayed():
                if safe_click_element(next_arrow_button):
                    time.sleep(3)  # Wait for page to load
                    return True
        except NoSuchElementException:
            pass
        
        # Try other common pagination selectors as fallback
        next_button_selectors = [
            "a[aria-label='Go to next page']",
            "button[aria-label='Go to next page']",
            ".pagination a[aria-label*='next']",
            ".pagination button[aria-label*='next']",
            ".page-item.next a",
            ".next",
            ".pagination-next",
            "button[aria-label*='next']",
            "a[aria-label*='next']",
            ".page-next",
            "[class*='next']"
        ]
        
        for selector in next_button_selectors:
            try:
                next_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for next_button in next_buttons:
                    if (next_button.is_enabled() and 
                        next_button.is_displayed() and 
                        not 'disabled' in next_button.get_attribute('class').lower()):
                        
                        if safe_click_element(next_button):
                            time.sleep(3)  # Wait for page to load
                            return True
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        # Try to find pagination info to see if we're on the last page
        try:
            pagination_info = self.driver.find_elements(By.CSS_SELECTOR, ".pagination-info, .page-info, [class*='pagination']")
            for info in pagination_info:
                print(f"Pagination info: {info.text}")
        except:
            pass
        
        return False
    
    def scrape_all_locations(self, base_url, start_page=1):
        """Scrape all locations from all pages starting from a specific page"""
        self.start_driver()
        
        try:
            print(f"Loading URL: {base_url}")
            self.driver.get(base_url)
            
            # Wait for initial page load
            time.sleep(5)
            
            # Navigate to the starting page if it's not page 1
            if start_page > 1:
                print(f"Navigating to page {start_page}...")
                for page_num in range(2, start_page + 1):
                    if not self.find_and_click_next_button():
                        print(f"Failed to navigate to page {start_page}. Starting from current page.")
                        break
                    print(f"Navigated to page {page_num}")
                    time.sleep(2)  # Brief delay between page navigations
            
            page_number = start_page
            max_retries = 3
            
            while True:
                print(f"Scraping page {page_number}...")
                
                # Check if driver is still responsive
                try:
                    self.driver.current_url
                except Exception as e:
                    print(f"Browser session lost, restarting driver... Error: {e}")
                    self.close_driver()
                    self.start_driver()
                    self.driver.get(base_url)
                    time.sleep(5)
                    # Navigate back to current page
                    for _ in range(page_number - 1):
                        if not self.find_and_click_next_button():
                            print("Failed to navigate back to current page")
                            return self.locations
                
                # Scrape current page with retry logic
                page_locations = []
                retry_count = 0
                
                while retry_count < max_retries:
                    try:
                        page_locations = self.scrape_current_page()
                        break  # Success, exit retry loop
                    except Exception as e:
                        retry_count += 1
                        if "invalid session id" in str(e).lower() or "session deleted" in str(e).lower():
                            print(f"Session error on page {page_number}, attempt {retry_count}/{max_retries}")
                            if retry_count < max_retries:
                                print("Restarting driver and retrying...")
                                self.close_driver()
                                self.start_driver()
                                self.driver.get(base_url)
                                time.sleep(5)
                                # Navigate back to current page
                                for _ in range(page_number - 1):
                                    if not self.find_and_click_next_button():
                                        print("Failed to navigate back to current page")
                                        return self.locations
                            else:
                                print(f"Max retries reached for page {page_number}, moving to next page")
                                break
                        else:
                            print(f"Non-session error on page {page_number}: {e}")
                            break
                
                if page_locations:
                    self.locations.extend(page_locations)
                    print(f"Found {len(page_locations)} locations on page {page_number}")
                    # Save this page's results immediately
                    self.save_page_to_csv(page_locations)
                else:
                    print(f"No locations found on page {page_number}")
                    
                    # If no locations found, try to debug
                    if page_number == start_page:
                        print("Debugging starting page...")
                        print("Page title:", self.driver.title)
                        print("Current URL:", self.driver.current_url)
                        
                        # Save page source for debugging
                        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                            f.write(self.driver.page_source)
                        print("Page source saved to debug_page_source.html")
                
                # Try to go to next page
                print("\nAttempting to navigate to next page...")
                if not self.find_and_click_next_button():
                    print("No more pages found or next button not clickable")
                    break
                
                # Add a small delay between pages to ensure proper loading
                time.sleep(3)
                page_number += 1
                
                # Safety break to avoid infinite loops
                if page_number > 50:
                    print("Reached maximum page limit (50)")
                    break
        
        finally:
            self.close_driver()
        
        return self.locations
    
    def save_page_to_csv(self, page_locations, filename='ssm_health_locations.csv'):
        """Save a single page of locations to CSV file"""
        if page_locations:
            df = pd.DataFrame(page_locations)
            # Ensure MSA column is present
            if 'msa' not in df.columns:
                df = self.msa_lookup.add_msa_to_dataframe(df)
            # Check if file exists to determine if we should write header
            file_exists = pd.io.common.file_exists(filename)
            df.to_csv(filename, mode='a', header=not file_exists, index=False)
            print(f"Saved {len(page_locations)} locations from current page to {filename}")
        else:
            print("No locations to save from current page")
    
    def save_to_csv(self, filename='ssm_health_locations.csv'):
        """Save all locations to CSV file"""
        if self.locations:
            df = pd.DataFrame(self.locations)
            # Ensure MSA column is present
            if 'msa' not in df.columns:
                df = self.msa_lookup.add_msa_to_dataframe(df)
            # Check if file exists to determine if we should write header
            file_exists = pd.io.common.file_exists(filename)
            df.to_csv(filename, mode='a', header=not file_exists, index=False)
            print(f"Saved {len(self.locations)} locations to {filename}")
        else:
            print("No locations to save")
    
    def save_to_json(self, filename='ssm_health_locations.json'):
        """Save locations to JSON file"""
        if self.locations:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.locations, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.locations)} locations to {filename}")
        else:
            print("No locations to save")

def main():
    """Main function to run the scraper"""
    url = "https://www.getcare.ssmhealth.com/locations?location=Chicago%2C+IL"
    
    scraper = SSMHealthLocationsScraper(headless=False)  # Set to True for headless mode
    
    try:
        locations = scraper.scrape_all_locations(url, start_page=20)
        
        if locations:
            print(f"\nSuccessfully scraped {len(locations)} locations!")
            
            # Display first few locations
            print("\nFirst 3 locations:")
            for i, location in enumerate(locations[:3]):
                print(f"\n{i+1}. {location['name']}")
                print(f"   Address: {location['address']}")
                print(f"   ZIP Code: {location['zip_code']}")
                print(f"   Phone: {location['phone']}")
                print(f"   Type: {location['type']}")
                print(f"   Specialty: {location['specialty']}")
                print(f"   Hours: {location['hours']}")
                print(f"   Distance: {location['distance']}")
                print(f"   MSA: {location['msa']}")
                print(f"   MSA Code: {location['msa_code']}")
                print(f"   MSA Source: {location['msa_source']}")
                print(f"   Link: {location['link']}")
                print(f"   Location ID: {location['location_id']}")
            
            # Save to files
            scraper.save_to_csv()
            scraper.save_to_json()
            
        else:
            print("No locations were scraped. Check the debug output above.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()