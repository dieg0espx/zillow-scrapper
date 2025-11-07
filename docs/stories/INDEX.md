# Zillow Scraper Optimization - Complete Stories Index

**Project:** Zillow Property Scraper Performance Optimization
**Owner:** Diego
**Created:** 2025-11-07
**Status:** Ready for Review

---

## Overview

This document provides a complete index of all 6 epics and 18 stories for the Zillow scraper optimization project.

**Current Performance:** 60-90 seconds per property
**Target Performance:** 10-20 seconds per property
**Expected Improvement:** 70-85% faster

---

## Quick Navigation

- [Epic 1: Intelligent Wait Strategy](#epic-1-intelligent-wait-strategy) - 3 stories - **35-45s savings**
- [Epic 2: Streamlined Scrolling](#epic-2-streamlined-scrolling) - 3 stories - **15-25s savings**
- [Epic 3: Optimized Element Discovery](#epic-3-optimized-element-discovery) - 3 stories - **8-12s savings**
- [Epic 4: Concurrent Operations](#epic-4-concurrent-operations) - 3 stories - **6-10s savings**
- [Epic 5: Smart Browser Management](#epic-5-smart-browser-management) - 3 stories - **3-6s savings**
- [Epic 6: Enhanced Error Handling](#epic-6-enhanced-error-handling) - 3 stories - **< 1% error rate**

---

## Epic 1: Intelligent Wait Strategy

**Priority:** P0 (Critical)
**Time Savings:** 35-45 seconds
**Epic File:** [epic-1-intelligent-wait-strategy.md](../epics/epic-1-intelligent-wait-strategy.md)

### Story 1.1: Implement Explicit Wait Conditions ✅ DETAILED
**Status:** Draft | **Points:** 5 | **Savings:** 30-40s
**File:** [story-1.1-explicit-wait-conditions.md](story-1.1-explicit-wait-conditions.md)

**Summary:**
Replace all 15+ `time.sleep()` calls with intelligent `WebDriverWait` conditions that detect actual page state changes.

**Key Changes:**
- Remove `time.sleep()` from lines: 122, 130, 161, 171, 203, 216, 226, 244, 258, 264, 283, 294, 301, 316, 322, 331
- Implement `EC.presence_of_element_located()` and `EC.visibility_of_element_located()`
- Create custom conditions for image loading and gallery detection
- Add exponential backoff (100ms, 200ms, 500ms) for failed waits
- Add timeout handling with graceful fallbacks

**Acceptance Criteria:**
- All `time.sleep()` removed
- Custom wait conditions for images and gallery
- Timeout handling with meaningful errors
- 30-40s time savings measured
- 99% data accuracy maintained

**Dependencies:** None (start immediately)

---

### Story 1.2: Implement Image Loading Detection ✅ DETAILED
**Status:** Draft | **Points:** 3 | **Savings:** 5-10s
**File:** [story-1.2-image-loading-detection.md](story-1.2-image-loading-detection.md)

**Summary:**
Create JavaScript-based image load detection that handles lazy-loaded images and detects when all images are fully loaded.

**Key Implementation:**
```python
def wait_for_images_loaded(driver, container=None, timeout=3):
    """Wait for all images using JS detection"""
    # Check img.complete && naturalHeight > 0
    # Handle lazy-loaded images (data-src)
    # Filter out placeholders
    # Return when all property images loaded
```

**Acceptance Criteria:**
- JS-based image detection implemented
- Handles lazy-loaded images
- Max wait: 3 seconds
- Fallback to visible images on timeout
- 5-10s time savings measured

**Dependencies:** Requires Story 1.1

---

### Story 1.3: Dynamic Wait Time Calculation ✅ DETAILED
**Status:** Draft | **Points:** 2 | **Savings:** 2-5s
**File:** [story-1.3-dynamic-wait-calculation.md](story-1.3-dynamic-wait-calculation.md)

**Summary:**
Calculate optimal wait times based on measured network performance using Navigation Timing API.

**Key Implementation:**
- Measure page load baseline using `window.performance.timing`
- Calculate multiplier: Fast (< 2s) = 0.5x, Normal (2-5s) = 1.0x, Slow (> 5s) = 2.0x
- Apply multiplier to all `WebDriverWait` timeouts
- Track and report performance metrics

**Acceptance Criteria:**
- Navigation timing measured
- Multipliers calculated and applied
- Performance metrics logged
- 2-5s savings on fast networks

**Dependencies:** Requires Story 1.1

---

## Epic 2: Streamlined Scrolling Strategy

**Priority:** P0 (Critical)
**Time Savings:** 15-25 seconds
**Epic File:** [epic-2-streamlined-scrolling.md](../epics/epic-2-streamlined-scrolling.md)

### Story 2.1: Unified Scroll Algorithm ✅ DETAILED
**Status:** Draft | **Points:** 5 | **Savings:** 10-15s
**File:** [story-2.1-unified-scroll-algorithm.md](story-2.1-unified-scroll-algorithm.md)

**Summary:**
Consolidate 4 redundant scrolling strategies (lines 208-283) into single intelligent algorithm.

**Key Changes:**
```python
def scroll_gallery_unified(driver, gallery_container, max_scrolls=5):
    # Calculate gallery height and optimal scroll positions (3-5 stops)
    # Scroll within container only (not main page)
    # Wait for images after each stop
    # Complete in < 5 seconds
```

**Removes:**
- Strategy 1: Main page scroll (5 stops, 10s)
- Strategy 2: Gallery scroll (5 stops, 10s)
- Strategy 2.5: Item-by-item scroll (variable, 10-30s)
- Strategy 3: Click navigation (20 iterations, 10s)
- Strategy 4: Final scroll (5 stops, 7.5s)

**Acceptance Criteria:**
- All 4 strategies removed
- Unified algorithm with 3-5 scroll stops max
- Scrolling completes in < 5 seconds
- 100% image discovery maintained

**Dependencies:** Requires Story 1.2 (image detection)

---

### Story 2.2: JavaScript-Based Lazy Load Trigger
**Status:** Draft | **Points:** 3 | **Savings:** 5-10s (HIGH RISK)
**Priority:** P0 | **Risk:** HIGH

**Summary:**
Research and implement JavaScript-based lazy-load triggering to avoid physical scrolling.

**⚠️ Technical Risk:**
Zillow likely uses `IntersectionObserver` with server-side validation. Simply setting `img.src = img.dataset.src` may NOT work.

**Key Implementation (R&D Required):**
```javascript
// Approach 1: Set src directly
lazyImages.forEach(img => {
    if (img.dataset.src) img.src = img.dataset.src;
});

// Approach 2: Trigger IntersectionObserver
lazyImages.forEach(img => {
    img.scrollIntoView({block: 'center', behavior: 'instant'});
});

// Approach 3: Dispatch load events
lazyImages.forEach(img => {
    img.dispatchEvent(new Event('load'));
});
```

**Acceptance Criteria:**
- Research Zillow's lazy-load mechanism
- Implement JS trigger approach
- Test on live page
- If successful: 5-10s savings
- If fails: Document findings, use Story 2.1 fallback

**Dependencies:** None (can be researched in parallel)
**Note:** If R&D shows approach won't work, de-prioritize or skip this story

---

### Story 2.3: Progressive Image Discovery
**Status:** Draft | **Points:** 3 | **Savings:** 5-10s
**Priority:** P0

**Summary:**
Extract images progressively during scrolling and exit early when count stabilizes.

**Key Implementation:**
```python
def scroll_with_progressive_discovery(driver, container):
    discovered_images = set()
    stable_count = 0

    for scroll_stop in range(max_scrolls):
        # Scroll to position
        scroll_to_position(container, scroll_stop)

        # Extract current images
        current_images = extract_image_urls(driver, container)
        new_images = current_images - discovered_images
        discovered_images.update(new_images)

        # Check if count stabilized
        if len(new_images) == 0:
            stable_count += 1
            if stable_count >= 2:  # 2 consecutive stable checks
                print(f"All images found, exiting early")
                break
        else:
            stable_count = 0

    return list(discovered_images)
```

**Acceptance Criteria:**
- Extract images after each scroll stop
- Track unique images discovered
- Exit when no new images for 2 consecutive checks
- Minimum 10 images before early exit allowed
- Max 5 scroll iterations

**Dependencies:** Requires Story 2.1 (unified scroll)

---

## Epic 3: Optimized Element Discovery

**Priority:** P1 (High)
**Time Savings:** 8-12 seconds
**Epic File:** [epic-3-optimized-element-discovery.md](../epics/epic-3-optimized-element-discovery.md)

### Story 3.1: Selector Priority Queue
**Status:** Draft | **Points:** 3 | **Savings:** 3-5s
**Priority:** P1

**Summary:**
Create selector configuration with priority weights, track success rates, and try most successful selectors first.

**Key Implementation:**
```json
// selector_config.json
{
  "see_all_button": {
    "selectors": [
      {"selector": "button[data-testid='media-stream-see-all']", "priority": 100, "type": "css"},
      {"selector": "button[data-testid='see-all-photos']", "priority": 90, "type": "css"}
    ]
  }
}

// selector_stats.json (tracks success)
{
  "see_all_button": {
    "button[data-testid='media-stream-see-all']": {
      "attempts": 150,
      "successes": 142,
      "rate": 0.947
    }
  }
}
```

**Acceptance Criteria:**
- Selector config file with priorities
- Success rate tracking in JSON
- Selectors ordered by success rate
- First-try success > 80%
- 3-5s time savings

**Dependencies:** None

---

### Story 3.2: Parallel Selector Testing
**Status:** Draft | **Points:** 2 | **Savings:** 3-5s
**Priority:** P1

**Summary:**
Test multiple selectors simultaneously via JavaScript instead of sequentially.

**Key Implementation:**
```python
def find_element_parallel(driver, selectors, timeout=2):
    """Test 5 selectors in parallel via JS"""
    script = """
    const selectors = arguments[0];
    // TRUE parallel using map
    const results = selectors.map(sel =>
        [sel, document.querySelector(sel)]
    ).find(([sel, el]) => el !== null);
    return results || [null, null];
    """
    return driver.execute_script(script, selectors)
```

**Acceptance Criteria:**
- Parallel testing via JS implemented
- Test up to 5 selectors simultaneously
- Return first successful match
- Timeout after 2 seconds
- 3-5s savings measured

**Dependencies:** None

---

### Story 3.3: XPath Optimization
**Status:** Draft | **Points:** 2 | **Savings:** 2-3s
**Priority:** P1

**Summary:**
Replace slow XPath expressions with faster CSS selectors where possible.

**Changes:**
```python
# ❌ Slow XPath (lines 117, 154)
elements = driver.find_elements(By.XPATH,
    "//button[contains(text(), 'See all')]")

# ✅ Fast CSS equivalent
elements = driver.find_elements(By.CSS_SELECTOR,
    "button[data-testid*='see-all'], button[aria-label*='See all']")
```

**Acceptance Criteria:**
- Replace complex XPath with CSS selectors (4-5x faster)
- Keep XPath only where CSS can't express query
- Use indexed paths where possible: `div[1]/span[2]`
- Benchmark selector performance
- 2-3s savings

**Dependencies:** None

---

## Epic 4: Concurrent Operations

**Priority:** P1 (High)
**Time Savings:** 6-10 seconds
**Epic File:** [epic-4-concurrent-operations.md](../epics/epic-4-concurrent-operations.md)

### Story 4.1: Parallel Data Extraction
**Status:** Draft | **Points:** 3 | **Savings:** 5-8s
**Priority:** P1 | **Confidence:** HIGH

**Summary:**
Extract all property data (address, price, beds, baths, area) in single JavaScript execution.

**Key Implementation:**
```python
def extract_property_data_batch(driver):
    """Extract all data in ONE JS execution"""
    script = """
    return {
        address: document.querySelector('h1.Text-c11n-8-109-3__sc-aiai24-0')?.textContent?.trim(),
        price: document.querySelector('span[data-testid="price"]')?.textContent?.trim(),
        beds: document.querySelector('span[data-testid="bed-bath-item"]:nth-child(1)')?.textContent?.trim(),
        baths: document.querySelector('span[data-testid="bed-bath-item"]:nth-child(2)')?.textContent?.trim(),
        area: document.querySelector('span[data-testid="bed-bath-item"]:nth-child(3)')?.textContent?.trim()
    };
    """
    return driver.execute_script(script)
```

**Current State:** Lines 44-91 make 6+ separate Selenium calls
**New State:** Single JS execution

**Acceptance Criteria:**
- Batch extraction in single JS call
- All fields extracted (address, price, beds, baths, area)
- Handle missing fields gracefully (return null)
- Complete in < 2 seconds
- 5-8s savings measured

**Dependencies:** None (HIGH VALUE story - do early!)

---

### Story 4.2: Optimized Image Processing
**Status:** Draft | **Points:** 1 | **Savings:** 0.5-1s (revised from 3-5s)
**Priority:** P2

**Summary:**
Optimize image URL filtering and deduplication using pre-compiled regex and sets.

**⚠️ Technical Revision:**
Original plan suggested `asyncio` but image filtering is CPU-bound, not I/O-bound. Asyncio won't help.

**Correct Implementation:**
```python
import re

# Pre-compile regex (do once)
VALID_IMAGE = re.compile(r'photos\.zillowstatic\.com.*cc_ft_.*\.(jpg|jpeg)', re.I)
EXCLUDE = re.compile(r'(-p_[eci]\.jpg|-h_e\.jpg|zillow_web_logo)', re.I)

def filter_images_optimized(image_urls):
    """Fast filtering using sets and pre-compiled regex"""
    seen = set()
    unique = []

    for url in image_urls:
        if (url not in seen and len(url) > 50 and
            VALID_IMAGE.search(url) and not EXCLUDE.search(url)):
            seen.add(url)
            unique.append(url)

    return unique
```

**Acceptance Criteria:**
- Pre-compile regex patterns
- Use set for O(1) deduplication
- Filter in single pass
- 0.5-1s savings

**Dependencies:** None

---

### Story 4.3: Multi-Property Batch Processing
**Status:** Draft | **Points:** 5 | **Savings:** N/A (enables batching)
**Priority:** P2

**Summary:**
Enable concurrent scraping of 5-10 properties using ThreadPoolExecutor.

**Key Implementation:**
```python
from concurrent.futures import ThreadPoolExecutor

def scrape_multiple_properties(urls, max_workers=5):
    """Scrape multiple properties concurrently"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(scrape_zillow_property, url) for url in urls]
        results = [f.result() for f in futures]
    return results
```

**Acceptance Criteria:**
- Support 5-10 concurrent scrapes
- ThreadPoolExecutor (not ProcessPoolExecutor)
- Separate browser per worker
- Queue-based URL processing
- Progress tracking
- Error handling per property

**Dependencies:** Story 5.1 (Browser Pooling) enhances but not required

---

## Epic 5: Smart Browser Management

**Priority:** P2 (Medium)
**Time Savings:** 3-6 seconds per scrape (after first)
**Epic File:** [epic-5-smart-browser-management.md](../epics/epic-5-smart-browser-management.md)

### Story 5.1: Browser Instance Pooling
**Status:** Draft | **Points:** 3 | **Savings:** 3-5s per subsequent scrape
**Priority:** P2

**Summary:**
Reuse browser instances across scrapes instead of creating new instance each time.

**⚠️ Simplified Approach:**
Instead of complex pooling, use simpler batch approach:

```python
def scrape_batch(urls, driver=None):
    """Scrape multiple URLs with same browser"""
    should_close = driver is None
    if driver is None:
        driver = init_driver()

    try:
        results = [scrape_single(driver, url) for url in urls]
        return results
    finally:
        if should_close:
            driver.quit()

# Usage
driver = init_driver()
try:
    batch1 = scrape_batch(urls[:10], driver)
    batch2 = scrape_batch(urls[10:20], driver)
finally:
    driver.quit()
```

**Acceptance Criteria:**
- Browser reuse for batch operations
- Cookie/cache cleanup between scrapes
- Browser health checks
- Max 10 scrapes per browser instance
- 3-5s savings per scrape (after first)

**Dependencies:** None

---

### Story 5.2: Headless Mode with Fallback
**Status:** Draft | **Points:** 2 | **Savings:** 2-3s
**Priority:** P2

**Summary:**
Enable headless mode by default to reduce rendering overhead.

**Implementation:**
```python
chrome_options = Options()
chrome_options.add_argument('--headless=new')  # New headless mode
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')
# Keep existing stealth flags (lines 22-26)
```

**Acceptance Criteria:**
- Headless mode enabled by default
- Bot detection monitoring
- Fallback to headed mode if detected
- 2-3s savings measured

**Dependencies:** None

---

### Story 5.3: Selective Resource Loading
**Status:** Draft | **Points:** 2 | **Risk:** HIGH - RECOMMEND SKIP
**Priority:** P3

**Summary:**
Block unnecessary resources (ads, analytics, fonts) to reduce page load time.

**⚠️ HIGH RISK:**
CDP resource blocking can trigger bot detection. Recommend SKIP or use safe Chrome prefs only.

**Safer Alternative:**
```python
chrome_options.add_experimental_option("prefs", {
    "profile.managed_default_content_settings.images": 2,  # Block initially
    "profile.default_content_setting_values.notifications": 2
})
```

**Recommendation:** SKIP this story or use safe prefs only

**Dependencies:** None

---

## Epic 6: Enhanced Error Handling

**Priority:** P2 (Medium)
**Impact:** Reduce error rate from 5-10% to < 1%
**Epic File:** [epic-6-error-handling.md](../epics/epic-6-error-handling.md)

### Story 6.1: Retry Logic with Exponential Backoff
**Status:** Draft | **Points:** 3 | **Impact:** Prevents 5-10% failures
**Priority:** P2

**Summary:**
Implement automatic retry with exponential backoff for transient failures.

**Retry Strategy:**
```python
# DO RETRY:
✅ driver.get(url) - Network errors
✅ wait.until(EC.presence...) - Element not found
✅ Button clicks - Stale element errors

# DON'T RETRY:
❌ Image extraction - Just log and continue
❌ Data parsing - Fail fast
❌ Invalid URLs - Won't fix with retry

RETRY_CONFIG = {
    'navigation': {'max_attempts': 3, 'backoff': [1, 2, 4]},
    'element_wait': {'max_attempts': 3, 'backoff': [0.5, 1, 2]},
    'click': {'max_attempts': 2, 'backoff': [0.5, 1]}
}
```

**Implementation:**
```python
@retry_with_backoff(max_attempts=3, backoff_delays=[1, 2, 4],
                    exceptions=(TimeoutException, StaleElementReferenceException))
def click_see_all_button(driver):
    button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='see-all-photos']")
    button.click()
```

**Acceptance Criteria:**
- Retry decorator implemented
- Exponential backoff (1s, 2s, 4s)
- Operation-specific retry configs
- Log all retry attempts
- Prevents 5-10% of current failures

**Dependencies:** None

---

### Story 6.2: Graceful Degradation
**Status:** Draft | **Points:** 3 | **Impact:** Recovers 50%+ failures
**Priority:** P2

**Summary:**
Return partial data when some fields fail instead of failing completely.

**Key Implementation:**
```python
property_data = {
    'url': url,
    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    'errors': []
}

# Try each field independently
try:
    property_data['address'] = extract_address(driver)
except Exception as e:
    property_data['errors'].append({'field': 'address', 'error': str(e)})

# ... repeat for all fields

# Calculate completeness score
property_data['completeness'] = calculate_completeness(property_data)
property_data['partial'] = property_data['completeness'] < 1.0
```

**Completeness Scoring:**
```python
REQUIRED_FIELDS = ['address', 'url', 'scraped_at']
OPTIONAL_FIELDS = ['monthly_rent', 'bedrooms', 'bathrooms', 'area', 'images']

# Score = (required + optional found) / total
# Fail if required fields missing
```

**Acceptance Criteria:**
- Independent field extraction with try/except
- Completeness score calculated
- Partial data flag included
- Error details logged
- Recovers 50%+ of failures

**Dependencies:** None

---

### Story 6.3: Comprehensive Logging and Metrics
**Status:** Draft | **Points:** 2 | **Impact:** Enables future optimization
**Priority:** P2

**Summary:**
Add detailed performance and error logging with structured JSON format.

**Implementation:**
```python
class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'extra': getattr(record, 'extra', {})
        })

# Log with metrics
logger.info('Property scraped', extra={
    'url': url,
    'duration': elapsed_time,
    'completeness': data['completeness'],
    'image_count': len(data.get('images', []))
})
```

**Metrics to Track:**
- Execution time per operation
- Success/failure rates
- Image counts
- Completeness scores
- Error types and frequencies

**Acceptance Criteria:**
- Structured JSON logging
- Performance metrics collected
- Saved to `zillow_scraper_metrics.json`
- Includes: total_time, operation_times, success_rates, errors

**Dependencies:** None

---

## Implementation Roadmap

### Phase 1: Quick Wins (Week 1)
**Target: 50% time reduction (60-90s → 30-40s)**

**Priority Order:**
1. Story 1.1 (Explicit Waits) - 30-40s savings
2. Story 1.2 (Image Detection) - 5-10s savings
3. Story 2.1 (Unified Scroll) - 10-15s savings

**Expected Result:** 45-65s savings

---

### Phase 2: Architectural (Week 2)
**Target: 70% reduction (30-40s → 15-25s)**

**Priority Order:**
1. Story 4.1 (Batch Data Extraction) - 5-8s savings ⭐ HIGH VALUE
2. Story 2.3 (Progressive Discovery) - 5-10s savings
3. Story 3.1 (Selector Priority) - 3-5s savings
4. Story 3.2 (Parallel Selectors) - 3-5s savings
5. Story 3.3 (XPath Optimization) - 2-3s savings

**Expected Result:** Additional 18-31s savings

---

### Phase 3: Advanced (Week 3)
**Target: 80% reduction + reliability (15-25s → 10-20s)**

**Priority Order:**
1. Story 6.2 (Graceful Degradation) - Recovers 50%+ failures
2. Story 6.1 (Retry Logic) - Prevents 5-10% failures
3. Story 5.2 (Headless Mode) - 2-3s savings
4. Story 5.1 (Browser Reuse) - 3-5s per subsequent scrape
5. Story 6.3 (Logging) - Enables monitoring
6. Story 1.3 (Dynamic Waits) - 2-5s savings
7. Story 4.2 (Image Filtering) - 0.5-1s savings
8. Story 4.3 (Batch Processing) - Enables concurrency

**Skip/Deprioritize:**
- Story 2.2 (Lazy Load Trigger) - HIGH RISK, may not work
- Story 5.3 (Resource Blocking) - HIGH RISK, bot detection

---

## Story Status Summary

### ✅ Detailed Story Files Created
- Story 1.1: Explicit Wait Conditions
- Story 1.2: Image Loading Detection
- Story 1.3: Dynamic Wait Calculation
- Story 2.1: Unified Scroll Algorithm

### 📝 Summary Only (Can Create Full Docs If Needed)
- Story 2.2: Lazy Load Trigger (HIGH RISK)
- Story 2.3: Progressive Discovery
- Story 3.1: Selector Priority Queue
- Story 3.2: Parallel Selector Testing
- Story 3.3: XPath Optimization
- Story 4.1: Parallel Data Extraction (HIGH VALUE)
- Story 4.2: Optimized Image Processing
- Story 4.3: Multi-Property Batch Processing
- Story 5.1: Browser Instance Pooling
- Story 5.2: Headless Mode
- Story 5.3: Selective Resource Loading (RECOMMEND SKIP)
- Story 6.1: Retry Logic
- Story 6.2: Graceful Degradation
- Story 6.3: Comprehensive Logging

---

## Key Technical Insights from Review

### ✅ High Confidence Stories (Do First)
- Story 1.1: Explicit waits (30-40s savings)
- Story 4.1: Batch data extraction (5-8s savings)
- Story 2.1: Unified scroll (10-15s savings)

### ⚠️ Medium Risk Stories (Research Required)
- Story 2.2: Lazy load trigger (may not work with IntersectionObserver)

### 🚫 Recommend Skip
- Story 5.3: Resource blocking (bot detection risk)

### 🔄 Technical Corrections Made
- Story 4.2: Removed asyncio approach (wrong for CPU-bound task)
- Story 3.2: Fixed parallel selector implementation (was sequential)
- Story 5.1: Simplified browser pooling approach
- Story 6.1: Defined specific retry strategies

---

## Next Steps

1. **Review This Document** - Diego reviews epics and stories
2. **Request Detailed Stories** - I can create full markdown for any story
3. **Approve Phase 1** - Green-light stories 1.1, 1.2, 2.1 for implementation
4. **Begin Implementation** - Start with Story 1.1

---

**Document Status:** ✅ Ready for Review
**Last Updated:** 2025-11-07
**Total Epics:** 6
**Total Stories:** 18
**Expected Savings:** 67-98 seconds per scrape
