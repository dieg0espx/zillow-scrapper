# Epic 5: Smart Browser Management

**Epic ID:** EPIC-5
**Priority:** P2 (Medium)
**Status:** Planning
**Owner:** Diego
**Created:** 2025-11-07

---

## Overview

Optimize browser lifecycle through instance reuse, headless mode, and selective resource loading to reduce setup overhead and page load times.

---

## Business Value

**Problem:** Current implementation creates a new browser instance for each scrape (8-12s overhead) and loads all page resources unnecessarily (ads, fonts, tracking scripts).

**Solution:** Reuse browser instances across scrapes, run in headless mode, and block non-essential resources.

**Impact:**
- **Time Savings:** 3-6 seconds per scrape (after first)
- **Resource Usage:** 40% reduction in bandwidth and memory
- **Scalability:** Enables efficient batch processing

---

## Goals

1. Implement browser instance pooling for reuse
2. Enable headless mode by default with fallback
3. Block unnecessary resources (ads, analytics, fonts)
4. Reduce browser setup time by 70%
5. Maintain stealth capabilities to avoid bot detection

---

## Success Metrics

- **Performance:** Browser setup < 3 seconds (vs 8-12s currently)
- **Resource Usage:** 40% reduction in page load size
- **Reliability:** No increase in bot detection
- **Efficiency:** Browser reuse for batch operations

---

## Technical Scope

### In Scope
- Browser pool class with get/release methods
- Headless mode configuration
- Resource blocking via Chrome flags
- Cookie/cache cleanup between scrapes
- Browser health checks and auto-restart

### Out of Scope
- Chrome DevTools Protocol (CDP) resource blocking (too risky for bot detection)
- Proxy rotation (separate concern)
- Browser fingerprint randomization (separate concern)

---

## Stories

1. **Story 5.1:** Browser Instance Pooling - 3-5s savings per subsequent scrape
2. **Story 5.2:** Headless Mode with Fallback - 2-3s savings
3. **Story 5.3:** Selective Resource Loading - SKIPPED (too risky)

**Total Epic Time Savings:** 3-6 seconds per scrape (after first)

---

## Dependencies

**Upstream:**
- Story 4.3 (Multi-Property Batch) benefits greatly from browser pooling
- All prior epics should be complete for best results

**Downstream:**
- None (final optimization epic)

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Browser reuse triggers bot detection | Medium | High | Clear cookies/cache between uses; monitor detection rates |
| Memory leaks from long-running browsers | Medium | Medium | Implement max-reuse limit (e.g., 10 scrapes); health checks |
| Headless mode behaves differently | Low | Medium | Comprehensive testing; fallback to headed mode |
| Resource blocking breaks functionality | HIGH | High | Use safe Chrome flags only (SKIP Story 5.3) |

---

## ⚠️ Technical Review Notes

**Story 5.1 (Browser Pooling) - COMPLEXITY vs BENEFIT:**

**Concern:** Browser pooling adds significant complexity:
- Cookie/cache cleanup is tricky
- Memory leaks from long-running browsers
- Zillow may detect reused sessions
- Debugging becomes harder

**Revised Approach - SIMPLER ALTERNATIVE:**
```python
# ✅ Simpler: Keep browser alive for batch, restart between batches
def scrape_batch(urls, driver=None):
    """Scrape multiple URLs with same browser instance"""
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
    batch1_results = scrape_batch(urls_batch1, driver)
    batch2_results = scrape_batch(urls_batch2, driver)
finally:
    driver.quit()
```

**Benefits:**
- Much simpler implementation
- Same performance benefit (3-5s savings)
- Easier debugging
- Less risk of state pollution

**Revised Time Savings:** 3-5s (unchanged, but simpler implementation)

---

**Story 5.3 (Resource Blocking) - HIGH RISK, RECOMMEND SKIP:**

**Problem:**
- CDP resource blocking can trigger bot detection
- May break dynamic content loading
- Unpredictable side effects

**Safer Alternative:**
```python
# ✅ Use built-in Chrome preferences (safer than CDP)
chrome_options.add_experimental_option("prefs", {
    "profile.managed_default_content_settings.images": 2,  # Block images initially
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_setting_values.media_stream": 2
})

# Existing safe flags (already in index.py)
chrome_options.add_argument("--disable-dev-shm-usage")  # line 23
chrome_options.add_argument("--no-sandbox")  # line 22
```

**Recommendation:** SKIP Story 5.3 or use safe Chrome prefs only

**Revised Risk:** High → Low (if using safe flags)

---

## Testing Requirements

### Unit Tests
- Test browser pool get/release
- Test cleanup between scrapes
- Test health check logic
- Test max-reuse enforcement

### Integration Tests
- Test browser reuse across 20 scrapes
- Monitor for memory leaks
- Test cookie/cache isolation
- Validate headless vs headed equivalence

### Performance Tests
- Benchmark browser setup time
- Test reuse time savings
- Measure memory usage over time
- Test page load time with/without resource blocking

### Security Tests
- Monitor bot detection rates
- Test with/without resource blocking
- Validate stealth mode still works

---

## Acceptance Criteria

- [ ] Browser pooling or batch reuse implemented
- [ ] Headless mode enabled by default
- [ ] Fallback to headed mode working
- [ ] Cookie/cache cleanup between scrapes
- [ ] Health checks and auto-restart implemented
- [ ] Browser setup < 3 seconds
- [ ] No increase in bot detection
- [ ] Memory usage stays reasonable (< 500MB per browser)
- [ ] Performance tests pass
- [ ] Documentation updated

---

## Implementation Notes

**Current State Analysis:**

Lines 20-30: Browser initialization
```python
# Currently: New browser every scrape (8-12s overhead)
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")  # Already present
chrome_options.add_argument("--disable-dev-shm-usage")  # Already present
# ... more options
driver = webdriver.Chrome(service=service, options=chrome_options)
```

**Headless Mode Addition (Story 5.2):**
```python
chrome_options.add_argument('--headless=new')  # New headless mode
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')  # Ensure consistent viewport
```

**Browser Reuse Implementation (Story 5.1 - Simplified):**
```python
def init_driver_with_options():
    """Initialize driver with all options"""
    chrome_options = Options()
    # ... all existing options
    chrome_options.add_argument('--headless=new')  # Add headless
    return webdriver.Chrome(service=service, options=chrome_options)

def cleanup_browser_state(driver):
    """Clean browser state between scrapes"""
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")

# Main batch scraping function
def scrape_multiple_properties(urls):
    driver = init_driver_with_options()
    results = []

    try:
        for i, url in enumerate(urls):
            if i > 0:  # Clean state between scrapes
                cleanup_browser_state(driver)
            result = scrape_zillow_property_with_driver(driver, url)
            results.append(result)
    finally:
        driver.quit()

    return results
```

---

## Related Documentation

- index.py:20-30 - Current browser initialization
- [Headless Chrome](https://developers.google.com/web/updates/2017/04/headless-chrome)
- [Chrome Options](https://peter.sh/experiments/chromium-command-line-switches/)
- [Selenium Performance](https://www.selenium.dev/documentation/webdriver/drivers/options/)

---

**Epic Status:** ✅ Ready for Story Breakdown
**Next Action:** Review Story 5.2 (lowest risk, good value)
**Priority:** Phase 3 (after Epic 1-4 complete)
**Note:** Story 5.1 simplified, Story 5.3 recommended skip
