from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import re

def scrape_zillow_property(url):
    """
    Scrape property data from Zillow URL using Selenium
    """
    driver = None
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Opening browser and navigating to Zillow...")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        
        # Extract property data
        property_data = {}
        
        # Wait for and extract address
        try:
            address_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.Text-c11n-8-109-3__sc-aiai24-0.cEHZrB')))
            property_data['address'] = address_element.text.strip()
            print(f"Found address: {property_data['address']}")
        except Exception as e:
            print(f"Could not find address: {e}")
        
        # Wait for and extract price
        try:
            price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-testid="price"]')))
            price_text = price_element.text.strip()
            # Extract just the number part
            price_match = re.search(r'\$([\d,]+)', price_text)
            if price_match:
                property_data['monthly_rent'] = price_match.group(1)
                print(f"Found price: ${property_data['monthly_rent']}")
        except Exception as e:
            print(f"Could not find price: {e}")
        
        # Wait for and extract beds, baths, area
        try:
            # Find all elements with the property details class
            detail_elements = driver.find_elements(By.CSS_SELECTOR, 'span.Text-c11n-8-109-3__sc-aiai24-0.styles__StyledValueText-fshdp-8-111-1__sc-12ivusx-1.cEHZrB.hCiIMl.--medium')
            
            if len(detail_elements) >= 1:
                property_data['beds'] = detail_elements[0].text.strip()
                print(f"Found beds: {property_data['beds']}")
            
            if len(detail_elements) >= 2:
                property_data['baths'] = detail_elements[1].text.strip()
                print(f"Found baths: {property_data['baths']}")
            
            if len(detail_elements) >= 3:
                property_data['area'] = detail_elements[2].text.strip()
                print(f"Found area: {property_data['area']}")
                
        except Exception as e:
            print(f"Could not find property details: {e}")
        
        # Extract all images
        try:
            print("Looking for 'See all' button to expand image gallery...")
            
            # Try to find and click "See all" or similar buttons
            see_all_selectors = [
                "button[data-testid='see-all-photos']",
                "button:contains('See all')",
                "button:contains('View all')",
                "button:contains('Show all')",
                "[data-testid*='see']",
                "[data-testid*='all']",
                "button[aria-label*='See all']",
                "button[aria-label*='View all']",
                "button[data-testid='media-stream-see-all']",
                "button[data-testid='gallery-see-all']",
                "button[data-testid='photos-see-all']"
            ]
            
            see_all_clicked = False
            for selector in see_all_selectors:
                try:
                    if ":contains(" in selector:
                        # Handle text-based selectors differently
                        elements = driver.find_elements(By.XPATH, f"//button[contains(text(), 'See all') or contains(text(), 'View all') or contains(text(), 'Show all') or contains(text(), 'See All') or contains(text(), 'View All')]")
                        if elements:
                            elements[0].click()
                            see_all_clicked = True
                            print("Clicked 'See all' button")
                            time.sleep(3)  # Wait for images to load
                            break
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            elements[0].click()
                            see_all_clicked = True
                            print("Clicked 'See all' button")
                            time.sleep(3)  # Wait for images to load
                            break
                except:
                    continue
            
            # Also try to find and click on navigation arrows or "Load more" buttons
            if not see_all_clicked:
                print("Looking for navigation arrows or load more buttons...")
                nav_selectors = [
                    "button[aria-label*='next']",
                    "button[aria-label*='Next']",
                    "button[data-testid*='next']",
                    "button[data-testid*='arrow']",
                    "button:contains('Load more')",
                    "button:contains('Show more')",
                    ".next-button",
                    ".arrow-right",
                    "[class*='next']",
                    "[class*='arrow']"
                ]
                
                for selector in nav_selectors:
                    try:
                        if ":contains(" in selector:
                            elements = driver.find_elements(By.XPATH, f"//button[contains(text(), 'Load more') or contains(text(), 'Show more')]")
                        else:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        if elements:
                            elements[0].click()
                            print("Clicked navigation/load more button")
                            time.sleep(2)
                            break
                    except:
                        continue
            
            if not see_all_clicked:
                print("No 'See all' button found, extracting visible images...")
            
            # Wait a bit more for all images to load
            print("Waiting for all images to load...")
            time.sleep(3)
            
            # Focus on scrolling within the "See all" gallery
            print("Scrolling within the 'See all' gallery...")
            try:
                # Find the expanded gallery container after clicking "See all"
                gallery_element = None
                gallery_selectors = [
                    "ul.hollywood-vertical-media-wall-container",
                    ".hollywood-vertical-media-wall-container",
                    "ul.StyledVerticalMediaWall-fshdp-8-111-1__sc-1liu0fm-3",
                    ".StyledVerticalMediaWall-fshdp-8-111-1__sc-1liu0fm-3",
                    "[data-testid='hollywood-vertical-media-wall']",
                    ".StyledVerticalMediaWall__StyledModalBody-fshdp-8-111-1__sc-1liu0fm-1",
                    "[data-testid='media-stream']",
                    ".media-stream"
                ]
                
                for selector in gallery_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            gallery_element = elements[0]
                            print(f"Found 'See all' gallery container: {selector}")
                            break
                    except:
                        continue
                
                if gallery_element:
                    # First, scroll the gallery into view
                    print("Scrolling gallery into view...")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gallery_element)
                    time.sleep(2)
                    
                    # Try multiple scrolling strategies to load all images
                    print("Trying multiple scrolling strategies...")
                    
                    # Strategy 1: Scroll the main page to trigger lazy loading with 5 stops
                    print("Strategy 1: Scrolling main page with 5 stops...")
                    page_height = driver.execute_script("return document.body.scrollHeight")
                    scroll_positions = [page_height * 0.2, page_height * 0.4, page_height * 0.6, page_height * 0.8, page_height]
                    
                    for i, position in enumerate(scroll_positions):
                        driver.execute_script(f"window.scrollTo(0, {int(position)});")
                        print(f"Main page scroll stop {i+1}/5 at {int(position)}px...")
                        time.sleep(2)  # Wait longer at each stop for images to load
                    
                    # Strategy 2: Scroll within the gallery element with 5 stops
                    print("Strategy 2: Scrolling within gallery with 5 stops...")
                    gallery_height = driver.execute_script("return arguments[0].scrollHeight", gallery_element)
                    gallery_positions = [gallery_height * 0.2, gallery_height * 0.4, gallery_height * 0.6, gallery_height * 0.8, gallery_height]
                    
                    for i, position in enumerate(gallery_positions):
                        driver.execute_script("arguments[0].scrollTop = arguments[1];", gallery_element, int(position))
                        print(f"Gallery scroll stop {i+1}/5 at {int(position)}px...")
                        time.sleep(2)  # Wait longer at each stop for images to load
                    
                    # Strategy 2.5: Target the media wall container specifically
                    print("Strategy 2.5: Targeting media wall container specifically...")
                    try:
                        # Look for the specific media wall container
                        media_wall = driver.find_element(By.CSS_SELECTOR, "ul.hollywood-vertical-media-wall-container")
                        if media_wall:
                            print("Found media wall container, scrolling through list items...")
                            # Get all list items in the media wall
                            list_items = media_wall.find_elements(By.CSS_SELECTOR, "li")
                            print(f"Found {len(list_items)} list items in media wall")
                            
                            # Scroll to each list item to trigger lazy loading
                            for i, item in enumerate(list_items):
                                try:
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
                                    print(f"Scrolled to list item {i+1}/{len(list_items)}")
                                    time.sleep(1)  # Wait for images to load
                                except:
                                    continue
                    except Exception as e:
                        print(f"Could not find media wall container: {e}")
                    
                    # Strategy 3: Try clicking through images to load more
                    print("Strategy 3: Clicking through images...")
                    try:
                        # Look for next/arrow buttons and click them
                        for i in range(20):
                            next_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='next'], button[aria-label*='Next'], .next, .arrow-right, [class*='next']")
                            if next_buttons:
                                next_buttons[0].click()
                                time.sleep(0.5)
                            else:
                                # Try clicking on images to advance
                                images = driver.find_elements(By.CSS_SELECTOR, "img[src*='photos.zillowstatic.com']")
                                if images and i < len(images):
                                    images[i].click()
                                    time.sleep(0.5)
                    except Exception as e:
                        print(f"Error during image navigation: {e}")
                    
                    # Strategy 4: Final comprehensive scroll with 5 stops
                    print("Strategy 4: Final comprehensive scroll with 5 stops...")
                    # Get updated heights after previous scrolling
                    final_page_height = driver.execute_script("return document.body.scrollHeight")
                    final_gallery_height = driver.execute_script("return arguments[0].scrollHeight", gallery_element)
                    
                    # Create 5 stops for both page and gallery
                    final_page_positions = [final_page_height * 0.1, final_page_height * 0.3, final_page_height * 0.5, final_page_height * 0.7, final_page_height * 0.9]
                    final_gallery_positions = [final_gallery_height * 0.1, final_gallery_height * 0.3, final_gallery_height * 0.5, final_gallery_height * 0.7, final_gallery_height * 0.9]
                    
                    for i in range(5):
                        # Scroll both main page and gallery to their respective positions
                        driver.execute_script(f"window.scrollTo(0, {int(final_page_positions[i])});")
                        driver.execute_script("arguments[0].scrollTop = arguments[1];", gallery_element, int(final_gallery_positions[i]))
                        print(f"Final comprehensive scroll stop {i+1}/5...")
                        time.sleep(1.5)  # Wait at each stop
                        
                else:
                    print("Could not find 'See all' gallery container, falling back to general scrolling with 5 stops...")
                    # Fallback to general page scrolling with 5 stops
                    fallback_page_height = driver.execute_script("return document.body.scrollHeight")
                    fallback_positions = [fallback_page_height * 0.2, fallback_page_height * 0.4, fallback_page_height * 0.6, fallback_page_height * 0.8, fallback_page_height]
                    
                    for i, position in enumerate(fallback_positions):
                        driver.execute_script(f"window.scrollTo(0, {int(position)});")
                        print(f"Fallback scroll stop {i+1}/5 at {int(position)}px...")
                        time.sleep(2)
                        
            except Exception as e:
                print(f"Error during gallery scrolling: {e}")
            
            # Wait for all images to load
            print("Waiting for all images to fully load...")
            time.sleep(3)
            
            # Try clicking through the image gallery to load more images
            print("Trying to navigate through image gallery...")
            try:
                # Look for image navigation elements
                nav_elements = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='next'], button[aria-label*='Next'], .next, .arrow-right, [class*='next']")
                
                # Try clicking through multiple images
                for i in range(10):  # Try clicking up to 10 times
                    try:
                        # Find and click next/arrow buttons
                        next_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='next'], button[aria-label*='Next'], .next, .arrow-right")
                        if next_buttons:
                            next_buttons[0].click()
                            time.sleep(1)
                        else:
                            # Try clicking on the image itself to advance
                            images = driver.find_elements(By.CSS_SELECTOR, "img[src*='photos.zillowstatic.com']")
                            if images:
                                images[0].click()
                                time.sleep(1)
                        break
                    except:
                        break
                        
            except Exception as e:
                print(f"Error navigating gallery: {e}")
            
            # Final wait for all images to load
            time.sleep(2)
            
            # Extract all image URLs with multiple attempts
            image_urls = []
            
            print("Searching for images with multiple methods...")
            
            # Method 1: Try multiple selectors for images, prioritizing the media wall container
            image_selectors = [
                "ul.hollywood-vertical-media-wall-container img",
                ".hollywood-vertical-media-wall-container img",
                "ul.StyledVerticalMediaWall-fshdp-8-111-1__sc-1liu0fm-3 img",
                "img[data-testid*='photo']",
                "img[src*='photos']",
                "img[alt*='photo']",
                "img[alt*='image']",
                ".media-stream img",
                ".photo-stream img",
                ".gallery img",
                "[data-testid='media-stream'] img",
                "img[src*='zillow']",
                "img[src*='photos.zillowstatic.com']",
                "img[data-testid='media-photo']",
                "[data-testid='media-photo'] img"
            ]
            
            for selector in image_selectors:
                try:
                    images = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"Selector '{selector}' found {len(images)} images")
                    for img in images:
                        src = img.get_attribute('src')
                        if src and src not in image_urls and 'http' in src:
                            image_urls.append(src)
                except:
                    continue
            
            # Method 2: Find all img tags and filter
            try:
                all_images = driver.find_elements(By.TAG_NAME, "img")
                print(f"Found {len(all_images)} total img elements")
                for img in all_images:
                    src = img.get_attribute('src')
                    if (src and 
                        src not in image_urls and 
                        'http' in src and 
                        'photos.zillowstatic.com' in src):
                        image_urls.append(src)
            except:
                pass
            
            # Method 3: Look for lazy-loaded images
            try:
                lazy_images = driver.find_elements(By.CSS_SELECTOR, "img[data-src], img[data-lazy-src]")
                print(f"Found {len(lazy_images)} lazy-loaded images")
                for img in lazy_images:
                    src = img.get_attribute('data-src') or img.get_attribute('data-lazy-src')
                    if src and src not in image_urls and 'http' in src:
                        image_urls.append(src)
            except:
                pass
            
            # Method 4: Target the media wall container specifically
            try:
                media_wall = driver.find_element(By.CSS_SELECTOR, "ul.hollywood-vertical-media-wall-container")
                if media_wall:
                    print("Extracting images from media wall container...")
                    # Get all images within the media wall
                    media_wall_images = media_wall.find_elements(By.CSS_SELECTOR, "img")
                    print(f"Found {len(media_wall_images)} images in media wall container")
                    
                    for img in media_wall_images:
                        src = img.get_attribute('src')
                        if src and src not in image_urls and 'http' in src:
                            image_urls.append(src)
                            
                    # Also check for images in list items
                    list_items = media_wall.find_elements(By.CSS_SELECTOR, "li")
                    for li in list_items:
                        li_images = li.find_elements(By.CSS_SELECTOR, "img")
                        for img in li_images:
                            src = img.get_attribute('src')
                            if src and src not in image_urls and 'http' in src:
                                image_urls.append(src)
            except Exception as e:
                print(f"Could not extract from media wall container: {e}")
            
            print(f"Total images found before filtering: {len(image_urls)}")
            
            # Remove duplicates and filter out non-property images
            unique_images = []
            for url in image_urls:
                if (url not in unique_images and
                    len(url) > 50 and
                    'photos.zillowstatic.com' in url and  # Only Zillow property photos
                    ('.jpg' in url or '.jpeg' in url) and  # Only JPG images
                    ('cc_ft_' in url) and  # Only main property photos (cc_ft_)
                    '-p_e.jpg' not in url and  # Exclude placeholder images
                    '-h_e.jpg' not in url and  # Exclude header images
                    'zillow_web_logo' not in url and  # Exclude logo images
                    '-p_i.jpg' not in url and  # Exclude icon images
                    '-p_c.jpg' not in url):  # Exclude other non-property images
                    unique_images.append(url)
            
            property_data['images'] = unique_images
            print(f"Found {len(unique_images)} images")
            
            # Print first few image URLs for verification
            for i, img_url in enumerate(unique_images[:3]):
                print(f"  Image {i+1}: {img_url[:80]}...")
                
        except Exception as e:
            print(f"Could not extract images: {e}")
            property_data['images'] = []
        
        # Add URL and timestamp
        property_data['url'] = url
        property_data['scraped_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        return property_data
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()

def save_to_json(data, filename='zillow_data.json'):
    """
    Save scraped data to JSON file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

if __name__ == "__main__":
    # URL to scrape
    url = "https://www.zillow.com/homedetails/9255-Swallow-Dr-Los-Angeles-CA-90069/20799705_zpid/"
    
    print("Starting Zillow scraper with Selenium...")
    property_data = scrape_zillow_property(url)
    
    if property_data:
        print("\n=== SCRAPED PROPERTY DATA ===")
        for key, value in property_data.items():
            print(f"{key}: {value}")
        
        # Save to JSON
        save_to_json(property_data)
        print(f"\n✅ Data successfully saved to zillow_data.json")
    else:
        print("❌ Failed to scrape data")