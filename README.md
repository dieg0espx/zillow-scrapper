# Zillow Property Scraper API

A FastAPI-based web scraper for extracting property details from Zillow listings, including address, price, bedrooms, bathrooms, area, and images.

## Features

- **Fast & Optimized**: 72% faster than traditional scraping methods (22s vs 79s)
- **Comprehensive Data**: Extracts address, price, beds, baths, area, and all property images
- **RESTful API**: Easy-to-use HTTP endpoints
- **Headless Browser**: Runs in background without opening browser windows
- **JSON Export**: Automatically saves scraped data to JSON files
- **Robust Extraction**: Multiple selector fallbacks ensure reliable data extraction

## Installation

### 1. Clone or Download the Repository

```bash
cd /Users/diego/Desktop/ZillowScrapper
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Start the API Server

```bash
python api.py
```

The server will start at `http://localhost:8000`

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## API Endpoints

### 1. Health Check

Check if the API is running:

```bash
GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-07T13:36:41.043185"
}
```

### 2. Scrape Property

Scrape a Zillow property by URL:

```bash
POST http://localhost:8000/scrape
Content-Type: application/json

{
  "url": "https://www.zillow.com/homedetails/9255-Swallow-Dr-Los-Angeles-CA-90069/20799705_zpid/"
}
```

**Response:**
```json
{
  "address": "9255 Swallow Dr, Los Angeles, CA 90069",
  "monthly_rent": "90,000",
  "bedrooms": "7",
  "bathrooms": "12",
  "area": "12,237 sqft",
  "images": [
    "https://photos.zillowstatic.com/fp/d3a7a5f14e029dc8ad0c1b468f2488c9-cc_ft_960.jpg",
    "https://photos.zillowstatic.com/fp/79bbd2f3284f54b7f29eac0687b5381f-cc_ft_576.jpg",
    ...
  ],
  "url": "https://www.zillow.com/...",
  "scraped_at": "2025-11-07 13:36:41"
}
```

## Usage Examples

### Using cURL

```bash
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.zillow.com/homedetails/9255-Swallow-Dr-Los-Angeles-CA-90069/20799705_zpid/"}'
```

### Using Python (requests)

```python
import requests

url = "http://localhost:8000/scrape"
payload = {
    "url": "https://www.zillow.com/homedetails/9255-Swallow-Dr-Los-Angeles-CA-90069/20799705_zpid/"
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Address: {data['address']}")
print(f"Price: ${data['monthly_rent']}/mo")
print(f"Bedrooms: {data['bedrooms']}")
print(f"Bathrooms: {data['bathrooms']}")
print(f"Area: {data['area']}")
print(f"Images: {len(data['images'])} found")
```

### Using JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/scrape', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://www.zillow.com/homedetails/9255-Swallow-Dr-Los-Angeles-CA-90069/20799705_zpid/'
  })
});

const data = await response.json();
console.log(data);
```

## Test the API

A test script is included to verify the API is working:

```bash
python test_api.py
```

This will:
1. Check the health endpoint
2. Scrape a test property
3. Display the results
4. Save the response to `api_response.json`

## Standalone Scripts

If you prefer to run the scraper without the API:

### Optimized Version (Recommended)
```bash
python index_optimized.py
```
- Execution time: ~22 seconds
- Saves to: `zillow_data_optimized.json`

### Original Version
```bash
python index.py
```
- Execution time: ~80 seconds
- Saves to: `zillow_data.json`

## API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

These provide:
- Interactive API testing interface
- Request/response schemas
- Example payloads
- All available endpoints

## Performance

### Optimization Highlights

| Metric | Original | Optimized | Improvement |
|--------|----------|-----------|-------------|
| **Execution Time** | ~79 seconds | **22 seconds** | **72% faster** |
| **Wait Strategy** | Fixed time.sleep() | Intelligent WebDriverWait | Dynamic |
| **Data Accuracy** | 100% | 100% | Maintained |
| **Images Extracted** | 75+ images | 75+ images | Same |

### How We Achieved 72% Speed Improvement

1. **Intelligent Waits**: Replaced 16 `time.sleep()` calls with WebDriverWait conditions
2. **JavaScript Detection**: Real-time image load detection using `img.complete && naturalHeight > 0`
3. **Reduced Scroll Waits**: 74 items × 0.2s = 14.8s (vs 74s with 1s each)
4. **Smart Conditions**: Custom wait conditions that return immediately when ready

## File Structure

```
ZillowScrapper/
├── api.py                      # FastAPI application
├── index.py                    # Original scraper (slower)
├── index_optimized.py          # Optimized scraper (72% faster)
├── test_api.py                 # API test script
├── debug_selectors.py          # Debug tool for finding selectors
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── venv/                       # Virtual environment
├── docs/                       # Documentation & performance results
│   ├── PERFORMANCE_RESULTS.md
│   ├── STORY-1.1-IMPLEMENTATION.md
│   └── zillow-scraper-optimization-plan.md
├── zillow_data.json           # Original scraper output
├── zillow_data_optimized.json # Optimized scraper output
├── api_response.json          # API test response
└── scraped_property_*.json    # API scrape outputs (timestamped)
```

## Technical Details

### Technologies Used
- **FastAPI**: Modern, high-performance web framework
- **Selenium**: Browser automation for dynamic content
- **ChromeDriver**: Headless Chrome browser
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

### Extraction Methods
1. **JavaScript Execution**: For fast, reliable data extraction
2. **Multiple Selector Fallbacks**: Ensures data is found even if page structure changes
3. **Custom Wait Conditions**: Intelligent waiting for dynamic content
4. **Image Detection**: Verifies images are actually loaded, not just present in DOM

### Selectors Used
- **Address**: `h1`, `h1[data-testid="main-header"]`
- **Price**: `span[data-testid="price"]`, `.ds-price span`
- **Property Details**: `[data-testid="bed-bath-sqft-fact-container"]`
- **Images**: `ul.hollywood-vertical-media-wall-container img`

## Troubleshooting

### Server Won't Start
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill the process if needed
kill -9 <PID>
```

### ChromeDriver Issues
```bash
# Update ChromeDriver
pip install --upgrade webdriver-manager
```

### Scraping Fails
- Check if the Zillow URL is valid and accessible
- Ensure stable internet connection
- Try increasing wait times in `api.py` (line 162)
- Check server logs for detailed error messages

### No Data Extracted
- Zillow may have updated their page structure
- Use `debug_selectors.py` to find new selectors:
  ```bash
  python debug_selectors.py
  ```

## Production Deployment

### Using Gunicorn (Recommended)

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:8000
```

### Environment Variables

```bash
# Optional: Configure host and port
export API_HOST=0.0.0.0
export API_PORT=8000
```

### Docker Deployment

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Chrome for headless mode
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver

COPY . .

CMD ["python", "api.py"]
```

## Rate Limiting & Best Practices

- **Respect Zillow's robots.txt**
- **Implement rate limiting** (recommended: 1 request per 5-10 seconds)
- **Use delays between requests** to avoid being blocked
- **Rotate user agents** if making many requests
- **Consider caching** results to reduce load

## License

This project is for educational purposes only. Please respect Zillow's Terms of Service and robots.txt when scraping their website.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Check the `docs/` folder for detailed implementation notes

## Changelog

### v1.0.0 (2025-11-07)
- Initial release
- FastAPI implementation
- Optimized scraping (72% faster)
- Comprehensive data extraction
- Headless browser support
- Automatic JSON export
- Interactive API documentation
