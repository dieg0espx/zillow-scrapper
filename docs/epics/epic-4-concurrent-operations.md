# Epic 4: Concurrent Operations

**Epic ID:** EPIC-4
**Priority:** P1 (High)
**Status:** Planning
**Owner:** Diego
**Created:** 2025-11-07

---

## Overview

Enable parallel processing of independent operations (data extraction, image processing, multi-property scraping) to eliminate sequential bottlenecks.

---

## Business Value

**Problem:** Current implementation extracts data sequentially (address → price → beds → baths → area → images), making 6+ separate Selenium calls that could run concurrently or be batched into a single operation.

**Solution:** Extract all property data in a single JavaScript execution, optimize image processing, and enable concurrent scraping of multiple properties.

**Impact:**
- **Time Savings:** 6-10 seconds per scrape
- **Scalability:** Enable batch processing of 10+ properties
- **Efficiency:** Reduce context switches and driver calls

---

## Goals

1. Extract all property data in single JS execution
2. Optimize image URL filtering/deduplication
3. Enable concurrent scraping of multiple properties
4. Reduce browser/driver overhead through batching
5. Maintain data accuracy while improving throughput

---

## Success Metrics

- **Performance:** Data extraction < 2 seconds (vs 5-8s currently)
- **Throughput:** 10+ concurrent property scrapes
- **Efficiency:** Single JS call vs 6+ Selenium calls
- **Scalability:** Linear performance scaling up to 10 workers

---

## Technical Scope

### In Scope
- Batch property data extraction via JavaScript
- Image URL filtering optimization
- Multi-property concurrent scraping
- Browser pool management for batch operations
- Progress tracking and error aggregation

### Out of Scope
- Distributed scraping across machines
- Async/await architecture (Selenium is synchronous)
- Image download/storage (only URL extraction)

---

## Stories

1. **Story 4.1:** Parallel Data Extraction - 5-8s savings ✅ HIGH VALUE
2. **Story 4.2:** Optimized Image Processing - 0.5-1s savings (revised from 3-5s)
3. **Story 4.3:** Multi-Property Batch Processing - Enables batch capability

**Total Epic Time Savings:** 6-10 seconds (single scrape) + batch capability

---

## Dependencies

**Upstream:**
- None (can start immediately for Stories 4.1 and 4.2)
- Story 5.1 (Browser Pooling) enhances Story 4.3 but not required

**Downstream:**
- Story 6.2 (Graceful Degradation) handles partial data extraction
- Epic 5 (Browser Management) optimizes batch processing further

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Batch JS extraction fails to find all elements | Low | High | Implement fallback to individual extraction; comprehensive testing |
| Concurrent scraping triggers rate limiting | Medium | High | Implement configurable concurrency; add delays between batches |
| Memory issues with many browser instances | Medium | Medium | Limit max workers to 10; implement browser pool cleanup |
| One failure crashes entire batch | Low | Medium | Isolated error handling per property; partial results return |

---

## ⚠️ Technical Review Notes

**Story 4.2 (Async Image Processing) - MISCONCEPTION:**

Initial plan proposed using `asyncio` for image processing. However:

**Problem:**
- Image filtering is CPU-bound regex matching, not I/O-bound
- `asyncio` doesn't help with CPU-bound tasks (GIL limitations)
- Adds complexity with minimal benefit

**Reality Check:**
```python
# ❌ This won't speed things up (CPU-bound, GIL-locked)
async def filter_images(urls):
    tasks = [asyncio.create_task(filter_url(url)) for url in urls]
    return await asyncio.gather(*tasks)

# ✅ This is fastest for CPU-bound filtering
unique_images = [
    url for url in image_urls
    if url not in seen and passes_filters(url)
]
```

**Revised Approach:**
- Use list comprehension (fastest for simple filtering)
- Pre-compile regex patterns
- Use set for O(1) deduplication

**Revised Time Savings:** 0.5-1s (not 3-5s)

---

**Story 4.3 (Batch Processing) - USE THREADING:**

```python
# ✅ Correct approach (I/O-bound, releases GIL)
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(scrape_property, url) for url in urls]
    results = [f.result() for f in futures]

# ❌ Don't use ProcessPoolExecutor (unnecessary overhead)
```

---

## Testing Requirements

### Unit Tests
- Test batch JS extraction logic
- Test image filtering accuracy
- Test concurrent worker management
- Test error isolation per property
- Mock Selenium responses

### Integration Tests
- Test on 20 properties with batch extraction
- Validate 100% data match with sequential
- Test concurrent scraping (5 properties)
- Test error handling in batch mode
- Validate memory usage stays reasonable

### Performance Tests
- Benchmark single extraction vs batch
- Test throughput at different concurrency levels (1, 3, 5, 10)
- Measure memory usage per browser instance
- Test rate limiting behavior

---

## Acceptance Criteria

- [ ] Batch JS extraction implemented
- [ ] Single call extracts all property fields
- [ ] Image filtering optimized
- [ ] Multi-property scraping working
- [ ] Concurrent workers configurable (1-10)
- [ ] Error handling isolates failures
- [ ] Progress tracking implemented
- [ ] Data accuracy ≥ 99% vs baseline
- [ ] Performance tests pass
- [ ] Documentation updated

---

## Implementation Notes

**Current State Analysis:**

Lines 44-91: Sequential property data extraction
```python
# Currently: 6+ separate operations
address = wait.until(EC.presence_of_element_located(...))  # Call 1
price = wait.until(EC.presence_of_element_located(...))    # Call 2
bed_bath_elements = driver.find_elements(...)              # Call 3
# ... more calls
```

**Batch Extraction Approach:**
```python
def extract_property_data_batch(driver):
    """Extract all property data in one JS execution"""
    script = """
    return {
        address: document.querySelector('h1.Text-c11n-8-109-3__sc-aiai24-0')?.textContent?.trim(),
        price: document.querySelector('span[data-testid="price"]')?.textContent?.trim(),
        beds: document.querySelector('span[data-testid="bed-bath-item"]:nth-child(1)')?.textContent?.trim(),
        baths: document.querySelector('span[data-testid="bed-bath-item"]:nth-child(2)')?.textContent?.trim(),
        area: document.querySelector('span[data-testid="bed-bath-item"]:nth-child(3)')?.textContent?.trim(),
        allFound: true
    };
    """
    return driver.execute_script(script)
```

**Benefits:**
- Single driver call vs 6+
- No waits between fields
- 5-8 second time savings
- Simpler code

---

**Optimized Image Filtering:**
```python
import re

# Pre-compile regex patterns (do once)
VALID_IMAGE_PATTERN = re.compile(r'photos\.zillowstatic\.com.*cc_ft_.*\.(jpg|jpeg)', re.IGNORECASE)
EXCLUDE_PATTERN = re.compile(r'(-p_[eci]\.jpg|-h_e\.jpg|zillow_web_logo)', re.IGNORECASE)

def filter_images_optimized(image_urls):
    """Fast image filtering using sets and pre-compiled regex"""
    seen = set()
    unique_images = []

    for url in image_urls:
        if (url not in seen and
            len(url) > 50 and
            VALID_IMAGE_PATTERN.search(url) and
            not EXCLUDE_PATTERN.search(url)):
            seen.add(url)
            unique_images.append(url)

    return unique_images
```

---

## Related Documentation

- index.py:44-91 - Current sequential extraction
- index.py:420-433 - Current image filtering
- [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor)
- [Selenium execute_script](https://selenium-python.readthedocs.io/api.html#selenium.webdriver.remote.webdriver.WebDriver.execute_script)

---

**Epic Status:** ✅ Ready for Story Breakdown
**Next Action:** Review Story 4.1 (highest value, lowest risk)
**Priority:** Phase 2 (after Epic 1 & 2 quick wins)
**Note:** Story 4.2 revised based on technical review
