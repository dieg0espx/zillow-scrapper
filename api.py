"""
FastAPI application for scraping Zillow properties
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import json
import time
import re
from datetime import datetime
from typing import List, Optional

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Zillow Property Scraper API",
    description="API for scraping Zillow property data including images, price, and details",
    version="1.0.0"
)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    print("⚠️  Warning: Supabase credentials not found in .env file")
    print("   Data will be saved to JSON files only")
    supabase_client = None
else:
    supabase_client: Client = create_client(supabase_url, supabase_key)
    print(f"✅ Connected to Supabase: {supabase_url}")


class ScrapeRequest(BaseModel):
    url: str

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.zillow.com/homedetails/9255-Swallow-Dr-Los-Angeles-CA-90069/20799705_zpid/"
            }
        }


class PropertyData(BaseModel):
    address: Optional[str] = None
    monthly_rent: Optional[str] = None
    bedrooms: Optional[str] = None
    bathrooms: Optional[str] = None
    area: Optional[str] = None
    images: List[str] = []
    url: str
    scraped_at: str


class ScrapeResponse(BaseModel):
    status: str
    message: str
    property_id: Optional[str] = None
    zillow_url: str
    items_saved: dict


class CustomConditions:
    """Custom wait conditions for Zillow scraper optimization"""

    @staticmethod
    def images_loaded_in_container(container_locator, min_images=5):
        """Wait for minimum number of images to load in container"""
        def _predicate(driver):
            try:
                container = driver.find_element(*container_locator)
                images = container.find_elements(By.TAG_NAME, "img")
                loaded_images = [
                    img for img in images
                    if img.get_attribute('src') and
                    'http' in img.get_attribute('src') and
                    'placeholder' not in img.get_attribute('src').lower()
                ]
                return container if len(loaded_images) >= min_images else False
            except:
                return False
        return _predicate

    @staticmethod
    def element_has_valid_src(element_locator):
        """Wait for image element to have valid src attribute"""
        def _predicate(driver):
            try:
                element = driver.find_element(*element_locator)
                src = element.get_attribute('src')
                return element if (src and 'http' in src and 'placeholder' not in src.lower()) else False
            except:
                return False
        return _predicate

    @staticmethod
    def gallery_loaded():
        """Wait for gallery container to be present and loaded"""
        gallery_selectors = [
            "ul.hollywood-vertical-media-wall-container",
            "[data-testid='hollywood-vertical-media-wall']",
            ".StyledVerticalMediaWall-fshdp-8-111-1__sc-1liu0fm-3"
        ]

        def _predicate(driver):
            for selector in gallery_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        return elements[0]
                except:
                    continue
            return False
        return _predicate


def wait_for_images_loaded(driver, container=None, timeout=5, min_images=1):
    """Wait for images to load using JavaScript detection"""
    script = """
    const container = arguments[0] || document;
    const images = Array.from(container.querySelectorAll('img'));

    const propertyImages = images.filter(img =>
        img.src &&
        img.src.includes('photos.zillowstatic.com') &&
        !img.src.includes('placeholder')
    );

    const loadedImages = propertyImages.filter(img =>
        img.complete && img.naturalHeight > 0
    );

    return {
        allLoaded: loadedImages.length >= arguments[1] && loadedImages.length === propertyImages.length,
        totalImages: propertyImages.length,
        loadedImages: loadedImages.length
    };
    """

    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = driver.execute_script(script, container, min_images)
            if result['allLoaded'] and result['totalImages'] > 0:
                return True
            time.sleep(0.3)
        return False
    except Exception as e:
        return False


def scrape_zillow_property(url: str) -> dict:
    """Scrape a Zillow property using the optimized scraper"""

    # Setup Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')  # Use new headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    property_data = {
        'url': url,
        'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        print(f"Starting scrape for: {url}")
        driver.get(url)

        # Wait for page to load - increased wait time
        print("Waiting for page to load...")
        time.sleep(5)  # Longer wait for dynamic content

        # Wait for main content to be present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            print("✓ Main content loaded")
        except:
            print("⚠ Timeout waiting for main content, continuing...")

        # Extract address - try multiple selectors
        try:
            address_selectors = [
                'h1',
                'h1[data-testid="main-header"]',
                '[data-testid="address"]',
                '.ds-address-container h1'
            ]
            for selector in address_selectors:
                try:
                    address_element = driver.find_element(By.CSS_SELECTOR, selector)
                    address_text = address_element.text.strip()
                    if address_text and len(address_text) > 10:  # Reasonable address length
                        property_data['address'] = address_text
                        print(f"✓ Found address: {property_data['address']}")
                        break
                except:
                    continue
        except Exception as e:
            print(f"Could not find address: {e}")

        # Extract price - try multiple selectors
        try:
            price_selectors = [
                'span[data-testid="price"]',
                '.ds-price span',
                'span[class*="price"]',
                '[data-testid="rent-price"]'
            ]
            for selector in price_selectors:
                try:
                    price_element = driver.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_element.text.strip()
                    price_match = re.search(r'\$?([\d,]+)', price_text)
                    if price_match:
                        property_data['monthly_rent'] = price_match.group(1)
                        print(f"✓ Found price: ${property_data['monthly_rent']}")
                        break
                except:
                    continue
        except Exception as e:
            print(f"Could not find price: {e}")

        # Extract property details (beds, baths, area)
        try:
            print("Extracting property details...")
            details_script = """
            const containers = Array.from(document.querySelectorAll('[data-testid="bed-bath-sqft-fact-container"]'));
            return containers.map(el => el.textContent.trim());
            """

            bed_bath_items = driver.execute_script(details_script)

            if bed_bath_items and len(bed_bath_items) >= 3:
                print(f"✓ Found {len(bed_bath_items)} property detail containers")

                # Bedrooms
                beds_text = bed_bath_items[0]
                beds_match = re.search(r'(\d+)', beds_text)
                if beds_match:
                    property_data['bedrooms'] = beds_match.group(1)
                    print(f"✓ Found bedrooms: {property_data['bedrooms']}")

                # Bathrooms
                baths_text = bed_bath_items[1]
                baths_match = re.search(r'(\d+(?:\.\d+)?)', baths_text)
                if baths_match:
                    property_data['bathrooms'] = baths_match.group(1)
                    print(f"✓ Found bathrooms: {property_data['bathrooms']}")

                # Area
                area_text = bed_bath_items[2]
                area_match = re.search(r'([\d,]+)', area_text)
                if area_match:
                    property_data['area'] = area_match.group(1) + ' sqft'
                    print(f"✓ Found area: {property_data['area']}")
        except Exception as e:
            print(f"Could not find property details: {e}")

        # Extract images
        try:
            print("Looking for 'See all' button...")

            see_all_selectors = [
                "button[data-testid='see-all-photos']",
                "button:contains('See all')",
                "button[aria-label*='See all']"
            ]

            see_all_clicked = False
            for selector in see_all_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        elements[0].click()
                        see_all_clicked = True
                        print("✓ Clicked 'See all' button")
                        time.sleep(0.5)

                        # Wait for gallery to load
                        try:
                            WebDriverWait(driver, 5).until(CustomConditions.gallery_loaded())
                            print("✓ Gallery appeared")
                        except:
                            print("Gallery timeout, continuing...")

                        wait_for_images_loaded(driver, timeout=3, min_images=3)
                        break
                except:
                    continue

            if see_all_clicked:
                # Scroll through the gallery
                print("Scrolling gallery...")
                try:
                    gallery_container = driver.find_element(By.CSS_SELECTOR, "ul.hollywood-vertical-media-wall-container")
                    driver.execute_script("arguments[0].scrollIntoView(true);", gallery_container)
                    time.sleep(0.3)

                    # Main page scrolls
                    for i in range(5):
                        scroll_pos = (i + 1) * 256
                        driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
                        time.sleep(0.3)
                        wait_for_images_loaded(driver, timeout=1, min_images=1)

                    # Scroll through list items
                    list_items = driver.find_elements(By.CSS_SELECTOR, "ul.hollywood-vertical-media-wall-container li")
                    print(f"Found {len(list_items)} list items")
                    for i, item in enumerate(list_items):
                        if i % 10 == 0:  # Scroll every 10 items
                            try:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
                                time.sleep(0.2)
                            except:
                                pass
                except Exception as e:
                    print(f"Scrolling error: {e}")

            # Extract all image URLs
            print("Extracting image URLs...")
            images_set = set()

            # Method 1: From media wall container
            try:
                media_wall_images = driver.find_elements(By.CSS_SELECTOR, "ul.hollywood-vertical-media-wall-container img")
                for img in media_wall_images:
                    src = img.get_attribute('src')
                    if src and 'photos.zillowstatic.com' in src:
                        images_set.add(src)
            except:
                pass

            # Method 2: All images with zillow photos
            try:
                all_images = driver.find_elements(By.CSS_SELECTOR, "img[src*='photos.zillowstatic.com']")
                for img in all_images:
                    src = img.get_attribute('src')
                    if src and 'photos.zillowstatic.com' in src and 'placeholder' not in src.lower():
                        images_set.add(src)
            except:
                pass

            property_data['images'] = sorted(list(images_set))
            print(f"✓ Found {len(property_data['images'])} unique images")

        except Exception as e:
            print(f"Error extracting images: {e}")

    finally:
        driver.quit()

    return property_data


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Zillow Property Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "POST /scrape": "Scrape a Zillow property by URL",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_property(request: ScrapeRequest):
    """
    Scrape a Zillow property by URL

    - **url**: The full Zillow property URL

    Returns the scraped property data including:
    - Address
    - Monthly rent
    - Bedrooms
    - Bathrooms
    - Area (sqft)
    - List of image URLs
    - Scrape timestamp
    """

    # Validate URL
    if 'zillow.com' not in request.url:
        raise HTTPException(status_code=400, detail="URL must be a valid Zillow property URL")

    try:
        # Scrape the property
        property_data = scrape_zillow_property(request.url)

        # Save to JSON file
        filename = f"scraped_property_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(property_data, f, indent=2)

        print(f"✅ Data saved to {filename}")

        # Save to Supabase if available
        database_id = None
        database_saved = False

        if supabase_client:
            try:
                # Prepare data for Supabase
                supabase_data = {
                    "address": property_data.get('address'),
                    "monthly_rent": property_data.get('monthly_rent'),
                    "bedrooms": property_data.get('bedrooms'),
                    "bathrooms": property_data.get('bathrooms'),
                    "area": property_data.get('area'),
                    "zillow_url": property_data.get('url'),
                    "images": property_data.get('images', []),
                    "scraped_at": property_data.get('scraped_at')
                }

                # Check if property already exists
                existing = supabase_client.table('properties')\
                    .select('id')\
                    .eq('zillow_url', property_data.get('url'))\
                    .execute()

                if existing.data:
                    # Update existing property
                    result = supabase_client.table('properties')\
                        .update(supabase_data)\
                        .eq('zillow_url', property_data.get('url'))\
                        .execute()
                    database_id = existing.data[0]['id']
                    database_saved = True
                    print(f"✅ Data updated in Supabase (ID: {database_id})")
                else:
                    # Insert new property
                    result = supabase_client.table('properties')\
                        .insert(supabase_data)\
                        .execute()
                    database_id = result.data[0]['id'] if result.data else None
                    database_saved = True
                    print(f"✅ Data saved to Supabase (ID: {database_id})")

            except Exception as e:
                print(f"⚠️  Warning: Could not save to Supabase: {e}")
                database_saved = False
        else:
            print("⚠️  Supabase not configured - data only saved to JSON")

        # Return success response with minimal data
        return ScrapeResponse(
            status="success",
            message="Property scraped and saved successfully",
            property_id=database_id,
            zillow_url=property_data.get('url'),
            items_saved={
                "address": property_data.get('address'),
                "monthly_rent": property_data.get('monthly_rent'),
                "bedrooms": property_data.get('bedrooms'),
                "bathrooms": property_data.get('bathrooms'),
                "area": property_data.get('area'),
                "images_count": len(property_data.get('images', [])),
                "saved_to_database": database_saved,
                "saved_to_json": filename
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
