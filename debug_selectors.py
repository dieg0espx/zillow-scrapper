"""
Debug script to find the correct selectors for beds/baths/area on Zillow
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import json

# Setup Chrome
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    # Navigate to the Zillow property
    url = "https://www.zillow.com/homedetails/9255-Swallow-Dr-Los-Angeles-CA-90069/20799705_zpid/"
    print(f"Loading: {url}")
    driver.get(url)
    time.sleep(3)  # Wait for page to load

    print("\n" + "="*80)
    print("DEBUGGING: Looking for beds/baths/area elements")
    print("="*80)

    # Method 1: Look for JSON-LD structured data
    print("\n--- Method 1: JSON-LD Structured Data ---")
    try:
        json_ld_script = driver.find_element(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
        json_data = json.loads(json_ld_script.get_attribute('innerHTML'))
        print(f"Found JSON-LD data: {json.dumps(json_data, indent=2)[:500]}")
        if 'numberOfBedrooms' in str(json_data):
            print(f"✓ Bedrooms might be in JSON-LD!")
    except Exception as e:
        print(f"No JSON-LD found: {e}")

    # Method 2: Search for text containing "bd", "ba", "sqft"
    print("\n--- Method 2: Text Search ---")
    script = """
    const bodyText = document.body.innerText;
    const lines = bodyText.split('\\n');
    const matches = lines.filter(line =>
        line.match(/\\d+\\s*bd/) ||
        line.match(/\\d+\\s*ba/) ||
        line.match(/\\d+.*sqft/i) ||
        line.includes('Bedrooms') ||
        line.includes('Bathrooms') ||
        line.includes('Square Feet')
    );
    return matches.slice(0, 10);  // Return first 10 matches
    """
    matches = driver.execute_script(script)
    print(f"Lines containing bed/bath/sqft keywords:")
    for match in matches:
        print(f"  - {match}")

    # Method 3: Find all elements with data-testid
    print("\n--- Method 3: Data-testid Attributes ---")
    elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid]')
    bed_bath_related = [el for el in elements if 'bed' in el.get_attribute('data-testid').lower() or 'bath' in el.get_attribute('data-testid').lower()]
    print(f"Found {len(bed_bath_related)} elements with bed/bath in data-testid:")
    for el in bed_bath_related[:5]:
        testid = el.get_attribute('data-testid')
        text = el.text[:50] if el.text else "(no text)"
        print(f"  - data-testid='{testid}': {text}")

    # Method 4: Search all spans with text
    print("\n--- Method 4: All Spans with Numeric Text ---")
    script = """
    const allSpans = Array.from(document.querySelectorAll('span'));
    const bedsMatch = allSpans.find(span => span.textContent.match(/\\d+\\s*bd/i));
    const bathsMatch = allSpans.find(span => span.textContent.match(/\\d+\\s*ba/i));
    const sqftMatch = allSpans.find(span => span.textContent.match(/\\d+.*sqft/i));

    return {
        beds: bedsMatch ? {
            text: bedsMatch.textContent,
            className: bedsMatch.className,
            id: bedsMatch.id,
            parent: bedsMatch.parentElement?.tagName + '.' + bedsMatch.parentElement?.className
        } : null,
        baths: bathsMatch ? {
            text: bathsMatch.textContent,
            className: bathsMatch.className,
            id: bathsMatch.id,
            parent: bathsMatch.parentElement?.tagName + '.' + bathsMatch.parentElement?.className
        } : null,
        sqft: sqftMatch ? {
            text: sqftMatch.textContent,
            className: sqftMatch.className,
            id: sqftMatch.id,
            parent: sqftMatch.parentElement?.tagName + '.' + sqftMatch.parentElement?.className
        } : null
    };
    """
    result = driver.execute_script(script)
    print("Spans with property details:")
    print(json.dumps(result, indent=2))

    # Method 5: Look in summary sections
    print("\n--- Method 5: Summary/Facts Sections ---")
    selectors_to_try = [
        '.ds-home-fact-list',
        '.ds-home-facts',
        '[data-testid="facts-list"]',
        '.summary-container',
        '.home-details',
        '.ds-data-col',
        '.ds-bed-bath-living-area',
        '.sc-bed-bath-area'
    ]
    for selector in selectors_to_try:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"✓ Found {len(elements)} elements with selector: {selector}")
                for i, el in enumerate(elements[:2]):
                    text = el.text[:200] if el.text else "(empty)"
                    print(f"    [{i}] {text}")
        except:
            pass

    # Method 6: Get page source snippet
    print("\n--- Method 6: HTML Snippet Around 'bd' ---")
    script = """
    const html = document.documentElement.outerHTML;
    const bdIndex = html.toLowerCase().indexOf(' bd');
    if (bdIndex > 0) {
        return html.substring(Math.max(0, bdIndex - 200), bdIndex + 200);
    }
    return "Pattern ' bd' not found in HTML";
    """
    snippet = driver.execute_script(script)
    print(f"HTML around ' bd': {snippet}")

    print("\n" + "="*80)
    print("Debug complete! Check output above for correct selectors.")
    print("="*80)

finally:
    driver.quit()
