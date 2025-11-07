# Epic 6: Enhanced Error Handling and Resilience

**Epic ID:** EPIC-6
**Priority:** P2 (Medium)
**Status:** Planning
**Owner:** Diego
**Created:** 2025-11-07

---

## Overview

Improve scraper reliability through retry logic, graceful degradation, and comprehensive logging to reduce error rate from 5-10% to < 1%.

---

## Business Value

**Problem:** Current implementation fails completely when any element is not found or network issues occur, resulting in 5-10% failure rate and complete data loss on failures.

**Solution:** Implement automatic retry with exponential backoff, graceful degradation to return partial data, and comprehensive logging for monitoring and debugging.

**Impact:**
- **Reliability:** Reduce failure rate from 5-10% to < 1%
- **Data Recovery:** Recover 50%+ of currently failed scrapes
- **Observability:** Detailed metrics for ongoing optimization
- **User Experience:** Partial data better than no data

---

## Goals

1. Implement retry logic with exponential backoff for transient failures
2. Enable graceful degradation to return partial data
3. Add comprehensive performance and error logging
4. Reduce complete failure rate to < 1%
5. Provide actionable metrics for further optimization

---

## Success Metrics

- **Reliability:** Complete failure rate < 1% (vs 5-10% currently)
- **Recovery:** Partial data returned in 50%+ of failure cases
- **Observability:** 100% of operations logged with timing
- **Quality:** Data completeness score for every scrape

---

## Technical Scope

### In Scope
- Retry decorator with configurable backoff
- Operation-specific retry strategies
- Graceful degradation for partial extraction
- Structured JSON logging
- Performance metrics collection
- Data completeness scoring

### Out of Scope
- Alerting/monitoring infrastructure (separate concern)
- Log aggregation/analysis tools
- Automated error recovery (manual review required)

---

## Stories

1. **Story 6.1:** Retry Logic with Exponential Backoff - Prevents 5-10% failures
2. **Story 6.2:** Graceful Degradation - Recovers 50%+ of failures
3. **Story 6.3:** Comprehensive Logging and Metrics - Enables future optimization

**Total Epic Impact:** < 1% failure rate + observability foundation

---

## Dependencies

**Upstream:**
- All other epics (this is the resilience layer on top)
- Benefits from all previous optimizations

**Downstream:**
- None (final epic)

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Retry logic increases execution time | Medium | Low | Set reasonable max retry limits (3 attempts, 10s total) |
| Partial data leads to incorrect analysis | Low | Medium | Include data completeness score; flag partial results |
| Logging overhead slows scraper | Low | Low | Use structured logging with minimal formatting |
| Retries trigger rate limiting | Low | Medium | Exponential backoff; monitor retry rates |

---

## ⚠️ Technical Review Notes

**Story 6.1 (Retry Logic) - NEEDS STRATEGY DEFINITION:**

The plan doesn't specify WHICH operations should be retried. Not all failures should trigger retries.

**Retry Strategy:**

✅ **DO RETRY:**
1. `driver.get(url)` - Network errors (ConnectionError, TimeoutException)
2. `wait.until(EC.presence...)` - Element not found (TimeoutException)
3. Button clicks - Stale element (StaleElementReferenceException)
4. Gallery container discovery - Not found immediately

❌ **DON'T RETRY:**
1. Image extraction - Just log and continue with what we have
2. Data parsing/regex - Fail fast and log
3. Invalid URLs - No point retrying
4. Permission errors - Won't fix with retry

**Retry Configuration:**
```python
RETRY_CONFIG = {
    'navigation': {'max_attempts': 3, 'backoff': [1, 2, 4]},
    'element_wait': {'max_attempts': 3, 'backoff': [0.5, 1, 2]},
    'click': {'max_attempts': 2, 'backoff': [0.5, 1]},
}
```

---

**Story 6.2 (Graceful Degradation) - IMPLEMENTATION DETAILS:**

**Data Completeness Scoring:**
```python
REQUIRED_FIELDS = ['address', 'url', 'scraped_at']  # Always required
OPTIONAL_FIELDS = ['monthly_rent', 'bedrooms', 'bathrooms', 'area', 'images']

def calculate_completeness(data):
    """Calculate data completeness score"""
    required_count = sum(1 for field in REQUIRED_FIELDS if data.get(field))
    optional_count = sum(1 for field in OPTIONAL_FIELDS if data.get(field))

    if required_count < len(REQUIRED_FIELDS):
        return 0.0  # Fail if required fields missing

    return (required_count + optional_count) / (len(REQUIRED_FIELDS) + len(OPTIONAL_FIELDS))

# Example output
{
    "address": "9255 Swallow Dr...",
    "monthly_rent": None,  # Failed to extract
    "bedrooms": "7",
    "bathrooms": "12",
    "area": None,  # Failed to extract
    "images": [...],  # Got 45 images
    "completeness": 0.714,  # 5/7 fields extracted
    "partial": true
}
```

---

## Testing Requirements

### Unit Tests
- Test retry decorator with various exceptions
- Test backoff timing accuracy
- Test graceful degradation logic
- Test completeness scoring
- Mock failure scenarios

### Integration Tests
- Test retry on live pages with network throttling
- Test partial data extraction
- Validate logging output structure
- Test with various failure modes

### Performance Tests
- Measure retry overhead
- Test max retry time limits
- Validate logging doesn't slow execution
- Test under high failure rates

### Regression Tests
- Ensure retries don't reduce success rate
- Validate partial data accuracy
- Test metrics accuracy

---

## Acceptance Criteria

- [ ] Retry decorator implemented
- [ ] Operation-specific retry strategies defined
- [ ] Exponential backoff working correctly
- [ ] Graceful degradation returns partial data
- [ ] Data completeness scoring implemented
- [ ] Structured JSON logging in place
- [ ] Performance metrics collected
- [ ] Complete failure rate < 1%
- [ ] Partial data recovery > 50%
- [ ] Documentation updated

---

## Implementation Notes

**Retry Decorator Implementation:**
```python
import time
from functools import wraps
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

def retry_with_backoff(max_attempts=3, backoff_delays=[1, 2, 4], exceptions=(TimeoutException,)):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        # Last attempt failed, re-raise
                        raise
                    delay = backoff_delays[min(attempt, len(backoff_delays)-1)]
                    print(f"Retry {attempt+1}/{max_attempts} after {delay}s: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_attempts=3, backoff_delays=[1, 2, 4],
                    exceptions=(TimeoutException, StaleElementReferenceException))
def click_see_all_button(driver):
    """Click see all button with retry logic"""
    button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='see-all-photos']")
    button.click()
```

---

**Graceful Degradation Pattern:**
```python
def scrape_zillow_property(url):
    """Scrape with graceful degradation"""
    driver = None
    property_data = {
        'url': url,
        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'errors': []
    }

    try:
        driver = init_driver()
        driver.get(url)

        # Try each field independently
        try:
            property_data['address'] = extract_address(driver)
        except Exception as e:
            property_data['errors'].append({'field': 'address', 'error': str(e)})

        try:
            property_data['monthly_rent'] = extract_price(driver)
        except Exception as e:
            property_data['errors'].append({'field': 'monthly_rent', 'error': str(e)})

        # ... continue for all fields

        # Calculate completeness
        property_data['completeness'] = calculate_completeness(property_data)
        property_data['partial'] = property_data['completeness'] < 1.0

        return property_data

    finally:
        if driver:
            driver.quit()
```

---

**Structured Logging:**
```python
import logging
import json

# Configure JSON logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        if hasattr(record, 'extra'):
            log_obj.update(record.extra)
        return json.dumps(log_obj)

# Usage
logger = logging.getLogger('zillow_scraper')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('zillow_scraper.log')
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# Log with metrics
logger.info('Property scraped', extra={
    'url': url,
    'duration': elapsed_time,
    'completeness': data['completeness'],
    'image_count': len(data.get('images', []))
})
```

---

## Related Documentation

- [Python Logging](https://docs.python.org/3/library/logging.html)
- [Selenium Exceptions](https://www.selenium.dev/selenium/docs/api/py/common/selenium.common.exceptions.html)
- [Exponential Backoff](https://en.wikipedia.org/wiki/Exponential_backoff)

---

**Epic Status:** ✅ Ready for Story Breakdown
**Next Action:** Review Story 6.2 (highest immediate value)
**Priority:** Phase 3 (after performance optimizations)
**Note:** Retry strategy defined; graceful degradation pattern specified
