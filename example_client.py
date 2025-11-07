"""
Simple example client for the Zillow Scraper API
"""
import requests
import json
import sys

API_URL = "http://localhost:8000"

def scrape_property(zillow_url: str):
    """
    Scrape a Zillow property and return the data

    Args:
        zillow_url: Full URL of the Zillow property

    Returns:
        dict: Property data including address, price, beds, baths, area, and images
    """
    print(f"Scraping: {zillow_url}")
    print("This may take 20-30 seconds...\n")

    try:
        response = requests.post(
            f"{API_URL}/scrape",
            json={"url": zillow_url},
            timeout=120  # 2 minute timeout
        )

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server.")
        print("Make sure the API server is running: python api.py")
        return None
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out. The scraping took too long.")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def display_property(data: dict):
    """Display property data in a nice format"""
    if not data:
        return

    print("=" * 70)
    print("PROPERTY DETAILS")
    print("=" * 70)
    print(f"Address:       {data.get('address', 'N/A')}")
    print(f"Monthly Rent:  ${data.get('monthly_rent', 'N/A')}")
    print(f"Bedrooms:      {data.get('bedrooms', 'N/A')}")
    print(f"Bathrooms:     {data.get('bathrooms', 'N/A')}")
    print(f"Area:          {data.get('area', 'N/A')}")
    print(f"Images Found:  {len(data.get('images', []))}")
    print(f"Scraped At:    {data.get('scraped_at', 'N/A')}")
    print("=" * 70)

    # Save to file
    filename = f"property_{data.get('address', 'unknown').replace(' ', '_').replace(',', '')}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Data saved to: {filename}")


if __name__ == "__main__":
    # Check if URL provided as argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Use default test URL
        url = "https://www.zillow.com/homedetails/9255-Swallow-Dr-Los-Angeles-CA-90069/20799705_zpid/"
        print("No URL provided, using test property\n")

    # Scrape the property
    property_data = scrape_property(url)

    # Display results
    if property_data:
        display_property(property_data)

        # Show first 3 image URLs
        if property_data.get('images'):
            print("\nSample Image URLs:")
            for i, img_url in enumerate(property_data['images'][:3], 1):
                print(f"  {i}. {img_url}")
            if len(property_data['images']) > 3:
                print(f"  ... and {len(property_data['images']) - 3} more")
