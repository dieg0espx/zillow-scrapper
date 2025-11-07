# Zillow Scraper Optimization Plan
**Project:** Zillow Property Scraper Performance Optimization
**Date:** 2025-11-07
**Owner:** Diego
**Status:** Planning Phase

---

## Executive Summary

This optimization project aims to reduce Zillow property scraper execution time by 70-85%, from 60-90 seconds to 10-20 seconds per property. The current implementation suffers from excessive wait times, redundant operations, and inefficient element discovery. This plan outlines a phased approach to systematically optimize performance while maintaining or improving data quality.

---

## Product Brief

### Problem Statement
The current Zillow scraper takes 60-90 seconds to scrape a single property due to:
- 50-80 seconds of hard-coded `time.sleep()` calls
- 4 redundant scrolling strategies executed sequentially
- Inefficient element searching with 15+ selector attempts per element type
- No parallelization or asynchronous operations
- Browser instance created/destroyed for each scrape
- Image filtering happens after all images are loaded

### Goals
1. **Primary Goal:** Reduce scraper execution time by 70-85%
2. **Secondary Goal:** Maintain or improve data extraction accuracy
3. **Tertiary Goal:** Enable batch processing of multiple properties

### Success Metrics
- Execution time: < 20 seconds per property (from 60-90s)
- Data accuracy: ≥ 99% match rate with current implementation
- Image extraction: All available images captured
- Error rate: < 1% failures
- Scalability: Support 10+ concurrent scrapes

### Target Users
- Data analysts scraping multiple properties
- Real estate professionals needing quick property data
- Automated monitoring systems

---

## Technical Analysis

### Current Performance Breakdown

| Operation | Current Time | % of Total |
|-----------|-------------|-----------|
| Browser setup & navigation | 8-12s | 15% |
| Initial element location | 5-8s | 10% |
| Image gallery expansion | 5-10s | 12% |
| Scrolling strategies (4x) | 40-50s | 60% |
| Image extraction & filtering | 5-10s | 10% |
| **Total** | **63-90s** | **100%** |

### Key Bottlenecks Identified

1. **Wait Time Bloat** - 50+ seconds of unnecessary sleeps
2. **Redundant Operations** - 4 scrolling strategies doing overlapping work
3. **Linear Execution** - No parallelization or async operations
4. **Inefficient Discovery** - Trying 15+ selectors sequentially
5. **Browser Overhead** - New instance per property
6. **Late Filtering** - Loading all images before filtering

---

## Optimization Epics

### Epic 1: Intelligent Wait Strategy
**Goal:** Replace hard-coded sleeps with smart, event-driven waits
**Impact:** 40-50 seconds time savings
**Priority:** P0 (Critical)

#### Story 1.1: Implement Explicit Wait Conditions
**As a** developer
**I want** to use Selenium's explicit waits with proper conditions
**So that** the scraper only waits as long as necessary for elements to load

**Acceptance Criteria:**
- Replace all `time.sleep()` calls with `WebDriverWait` and `expected_conditions`
- Implement custom wait conditions for image loading
- Add timeout handling with fallback logic
- Maximum wait time: 2 seconds per operation
- Document all wait conditions used

**Technical Details:**
- Use `EC.presence_of_element_located()` for element waits
- Use `EC.visibility_of_element_located()` for visible elements
- Create custom condition for image src attribute population
- Implement exponential backoff for failed waits (100ms, 200ms, 500ms)

**Estimated Time Savings:** 30-40 seconds

---

#### Story 1.2: Implement Image Loading Detection
**As a** scraper
**I want** to detect when images have finished loading
**So that** I don't wait longer than necessary

**Acceptance Criteria:**
- Create JavaScript-based image load detection
- Implement lazy-load detection mechanism
- Add batch image load verification
- Maximum wait: 3 seconds for all images
- Fallback to current visible images if timeout

**Technical Details:**
```python
def wait_for_images_loaded(driver, timeout=3):
    """Wait for all images to load using JS"""
    script = """
    return Array.from(document.images).every(img =>
        img.complete && img.naturalHeight !== 0
    );
    """
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(script)
    )
```

**Estimated Time Savings:** 5-10 seconds

---

#### Story 1.3: Dynamic Wait Time Calculation
**As a** developer
**I want** to calculate optimal wait times based on network performance
**So that** the scraper adapts to different network conditions

**Acceptance Criteria:**
- Measure page load time on initial navigation
- Calculate dynamic wait multipliers (0.5x to 2x)
- Apply multipliers to all subsequent waits
- Track and log actual vs expected wait times
- Provide performance metrics after scrape

**Technical Details:**
- Record navigation timing API metrics
- Calculate page load baseline
- Adjust wait timeouts dynamically
- Log performance metrics to JSON

**Estimated Time Savings:** 5-10 seconds (variable)

---

### Epic 2: Streamlined Scrolling Strategy
**Goal:** Consolidate redundant scrolling into single optimized approach
**Impact:** 25-35 seconds time savings
**Priority:** P0 (Critical)

#### Story 2.1: Unified Scroll Algorithm
**As a** developer
**I want** a single intelligent scrolling strategy
**So that** I eliminate redundant scrolling operations

**Acceptance Criteria:**
- Remove 4 separate scrolling strategies
- Implement single adaptive scroll algorithm
- Target media wall container directly
- Use viewport-based progressive scrolling
- Complete scrolling in < 5 seconds

**Technical Details:**
- Identify primary media wall container once
- Calculate optimal scroll positions (3-5 stops max)
- Scroll only within the gallery container
- Use `requestAnimationFrame` for smooth scrolling
- Trigger lazy-load observers programmatically

**Estimated Time Savings:** 30-40 seconds

---

#### Story 2.2: JavaScript-Based Lazy Load Trigger
**As a** developer
**I want** to trigger lazy-loaded images via JavaScript
**So that** I don't need to physically scroll

**Acceptance Criteria:**
- Identify lazy-load mechanism used (Intersection Observer, data-src, etc.)
- Implement JavaScript to trigger all lazy loads at once
- Verify all images are loaded after trigger
- Fallback to minimal scrolling if JS trigger fails
- Complete in < 2 seconds

**Technical Details:**
```python
def trigger_lazy_load(driver):
    """Trigger all lazy-loaded images via JS"""
    script = """
    // Find all lazy images
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    // Force load by setting src
    lazyImages.forEach(img => {
        if (img.dataset.src) img.src = img.dataset.src;
        // Dispatch events to trigger observers
        img.dispatchEvent(new Event('load'));
    });
    """
    driver.execute_script(script)
```

**Estimated Time Savings:** 20-30 seconds

---

#### Story 2.3: Progressive Image Discovery
**As a** developer
**I want** to discover and extract images progressively during scrolling
**So that** I can exit early once all images are found

**Acceptance Criteria:**
- Extract image URLs during scrolling
- Track unique images discovered
- Exit scrolling when count stabilizes (no new images in 2 consecutive checks)
- Maximum scroll iterations: 5
- Minimum images before early exit: 10

**Technical Details:**
- Maintain set of discovered image URLs
- Check for new images after each scroll stop
- Exit if `len(current_images) == len(previous_images)` for 2 iterations
- Log discovery progression

**Estimated Time Savings:** 5-15 seconds

---

### Epic 3: Optimized Element Discovery
**Goal:** Replace sequential selector attempts with intelligent discovery
**Impact:** 8-12 seconds time savings
**Priority:** P1 (High)

#### Story 3.1: Selector Priority Queue
**As a** developer
**I want** to try most likely selectors first
**So that** I minimize failed lookup attempts

**Acceptance Criteria:**
- Order selectors by success probability (most common first)
- Implement early exit on first match
- Log successful selectors for learning
- Maintain success rate statistics
- Update selector order based on success rates

**Technical Details:**
- Create selector configuration file with priority weights
- Track selector success rates in JSON
- Re-order selectors dynamically based on history
- Use most recently successful selector first

**Estimated Time Savings:** 3-5 seconds

---

#### Story 3.2: Parallel Selector Testing
**As a** developer
**I want** to test multiple selectors simultaneously
**So that** I find elements faster

**Acceptance Criteria:**
- Test up to 5 selectors in parallel using JavaScript
- Return first successful match
- Timeout after 2 seconds
- Fallback to sequential on timeout
- Log which selector succeeded

**Technical Details:**
```python
def find_element_parallel(driver, selectors, timeout=2):
    """Test multiple selectors in parallel via JS"""
    script = f"""
    const selectors = {json.dumps(selectors)};
    for (let selector of selectors) {{
        const element = document.querySelector(selector);
        if (element) return [selector, element.textContent];
    }}
    return [null, null];
    """
    return driver.execute_script(script)
```

**Estimated Time Savings:** 3-5 seconds

---

#### Story 3.3: XPath Optimization
**As a** developer
**I want** to use optimized XPath expressions
**So that** element lookup is faster

**Acceptance Criteria:**
- Replace complex XPath with CSS selectors where possible
- Use indexed XPath for known structures
- Avoid `//` (descendant) in favor of direct paths
- Benchmark selector performance
- Document selector performance metrics

**Technical Details:**
- Prefer CSS selectors (4-5x faster than XPath)
- Use `contains()` only when necessary
- Index into known structures: `div[1]/span[2]` vs `//div//span`
- Cache compiled XPath expressions

**Estimated Time Savings:** 2-3 seconds

---

### Epic 4: Concurrent Operations
**Goal:** Enable parallel processing of independent operations
**Impact:** 10-15 seconds time savings
**Priority:** P1 (High)

#### Story 4.1: Parallel Data Extraction
**As a** developer
**I want** to extract property details and images concurrently
**So that** operations don't block each other

**Acceptance Criteria:**
- Extract basic property data (address, price, beds, baths) in parallel
- Use JavaScript to extract all data in single execution
- Reduce multiple find_element calls to single batch operation
- Complete all extractions in < 2 seconds
- Handle missing fields gracefully

**Technical Details:**
```python
def extract_property_data_batch(driver):
    """Extract all property data in one JS execution"""
    script = """
    return {
        address: document.querySelector('h1.Text-c11n-8-109-3__sc-aiai24-0')?.textContent,
        price: document.querySelector('span[data-testid="price"]')?.textContent,
        beds: document.querySelector('span[data-testid="bed-bath-item"]:nth-child(1)')?.textContent,
        baths: document.querySelector('span[data-testid="bed-bath-item"]:nth-child(2)')?.textContent,
        area: document.querySelector('span[data-testid="bed-bath-item"]:nth-child(3)')?.textContent
    };
    """
    return driver.execute_script(script)
```

**Estimated Time Savings:** 5-8 seconds

---

#### Story 4.2: Async Image Processing
**As a** developer
**I want** to process and filter images asynchronously
**So that** image operations don't block data extraction

**Acceptance Criteria:**
- Use asyncio for image URL validation
- Process images in batches of 10
- Filter and deduplicate concurrently
- Return results in < 2 seconds
- Maintain original order if needed

**Technical Details:**
- Use `asyncio.gather()` for parallel processing
- Implement async URL validation
- Async regex matching for filtering
- Deduplicate using sets

**Estimated Time Savings:** 3-5 seconds

---

#### Story 4.3: Multi-Property Batch Processing
**As a** developer
**I want** to scrape multiple properties concurrently
**So that** I can process large datasets efficiently

**Acceptance Criteria:**
- Support concurrent scraping of 5-10 properties
- Each scrape runs in separate browser context
- Implement resource pooling (max 10 browsers)
- Queue-based job management
- Progress tracking and error handling

**Technical Details:**
- Use `concurrent.futures.ThreadPoolExecutor`
- Browser pool management with context manager
- Queue-based URL processing
- Aggregate results and error tracking

**Estimated Time Savings:** Not applicable to single scrape (enables batch processing)

---

### Epic 5: Smart Browser Management
**Goal:** Optimize browser lifecycle and reuse
**Impact:** 5-10 seconds time savings per subsequent scrape
**Priority:** P2 (Medium)

#### Story 5.1: Browser Instance Pooling
**As a** developer
**I want** to reuse browser instances across multiple scrapes
**So that** I avoid repeated setup overhead

**Acceptance Criteria:**
- Implement browser pool with configurable size (default: 3)
- Reuse browser instances for multiple URLs
- Clear cookies/cache between scrapes
- Handle browser crashes gracefully
- Auto-restart failed instances

**Technical Details:**
- Create `BrowserPool` class with get/release methods
- Use context manager for automatic cleanup
- Implement health checks before reuse
- Track instance usage statistics

**Estimated Time Savings:** 5-8 seconds per scrape (after first)

---

#### Story 5.2: Headless Mode with Fallback
**As a** developer
**I want** to run in headless mode by default
**So that** browser rendering overhead is minimized

**Acceptance Criteria:**
- Enable headless mode by default
- Add `--disable-gpu` and `--no-sandbox` flags
- Detect bot detection and fallback to headed mode
- Add user-agent rotation
- Implement stealth mode flags

**Technical Details:**
```python
chrome_options = Options()
chrome_options.add_argument('--headless=new')  # New headless mode
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # Disable images initially
chrome_options.add_argument('--disable-dev-shm-usage')
```

**Estimated Time Savings:** 2-3 seconds

---

#### Story 5.3: Selective Resource Loading
**As a** developer
**I want** to block unnecessary resources (ads, fonts, tracking scripts)
**So that** page load time is reduced

**Acceptance Criteria:**
- Block ads, analytics, and tracking scripts
- Load images only when needed
- Disable fonts and stylesheets initially
- Allow critical resources only
- Maintain data extraction functionality

**Technical Details:**
- Use Chrome DevTools Protocol to block resource types
- Implement request interception
- Whitelist only `photos.zillowstatic.com` domain
- Block `doubleclick`, `analytics`, `tagmanager`, etc.

**Estimated Time Savings:** 3-5 seconds

---

### Epic 6: Enhanced Error Handling and Resilience
**Goal:** Improve reliability and reduce failed scrapes
**Impact:** Reduce error rate from 5-10% to < 1%
**Priority:** P2 (Medium)

#### Story 6.1: Retry Logic with Exponential Backoff
**As a** developer
**I want** automatic retry with exponential backoff
**So that** transient failures don't result in data loss

**Acceptance Criteria:**
- Retry failed operations up to 3 times
- Implement exponential backoff (1s, 2s, 4s)
- Log all retry attempts
- Different retry strategies for different failure types
- Maximum total retry time: 10 seconds

**Technical Details:**
- Use decorator pattern for retry logic
- Separate retry configs for network vs element errors
- Track retry statistics
- Circuit breaker for repeated failures

**Estimated Time Savings:** Prevents 5-10% of failed scrapes

---

#### Story 6.2: Graceful Degradation
**As a** developer
**I want** partial data extraction when some elements fail
**So that** I get maximum data even with failures

**Acceptance Criteria:**
- Continue scraping even if some fields fail
- Mark missing fields with `null` or default values
- Log which fields failed extraction
- Return partial data with status indicator
- Provide data quality score (% fields extracted)

**Technical Details:**
- Try/except blocks for each field
- Aggregate field extraction results
- Calculate completeness score
- Include metadata in output JSON

**Estimated Time Savings:** Recovers 50% of failed scrapes

---

#### Story 6.3: Comprehensive Logging and Metrics
**As a** developer
**I want** detailed performance and error logging
**So that** I can monitor and optimize further

**Acceptance Criteria:**
- Log execution time for each operation
- Track success/failure rates per operation
- Generate performance report after each scrape
- Log to structured format (JSON)
- Include timestamp, duration, status for each step

**Technical Details:**
- Use Python `logging` with JSON formatter
- Create performance profiler decorator
- Save metrics to `zillow_scraper_metrics.json`
- Include: total_time, operation_times, success_rates, errors

**Estimated Time Savings:** N/A (enables future optimization)

---

## Implementation Roadmap

### Phase 1: Quick Wins (Week 1)
**Target: 50% time reduction**
- Epic 1: Intelligent Wait Strategy (Stories 1.1, 1.2)
- Epic 2: Streamlined Scrolling (Stories 2.1, 2.2)

**Expected Result:** 60-90s → 30-40s

---

### Phase 2: Architectural Improvements (Week 2)
**Target: 70% time reduction**
- Epic 3: Optimized Element Discovery (All stories)
- Epic 4: Concurrent Operations (Stories 4.1, 4.2)

**Expected Result:** 30-40s → 15-25s

---

### Phase 3: Advanced Optimization (Week 3)
**Target: 80% time reduction**
- Epic 5: Smart Browser Management (All stories)
- Epic 6: Error Handling (All stories)
- Epic 4: Story 4.3 (Batch processing)

**Expected Result:** 15-25s → 10-20s + batch capability

---

## Success Criteria

### Performance Targets
- ✅ Single property scrape: < 20 seconds (from 60-90s)
- ✅ Batch processing: 10+ properties concurrently
- ✅ Data accuracy: ≥ 99% match with current implementation
- ✅ Error rate: < 1%
- ✅ Image extraction: 100% of available images

### Quality Gates
Each epic must pass:
1. **Performance Test:** Execution time meets target
2. **Data Validation:** Extracted data matches baseline (10 sample properties)
3. **Error Rate Test:** < 1% failures over 100 scrapes
4. **Code Review:** Peer review completed
5. **Documentation:** README and inline docs updated

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Zillow changes selectors | Medium | High | Implement robust selector fallbacks, monitoring |
| Bot detection blocks scraper | Medium | High | Implement stealth mode, rate limiting, proxy support |
| Image extraction breaks | Low | Medium | Comprehensive testing, fallback mechanisms |
| Performance regression | Low | Medium | Benchmark tests, performance CI checks |
| Data accuracy issues | Low | High | Validation suite, A/B testing with current version |

---

## Testing Strategy

### Unit Tests
- Test each optimization function independently
- Mock Selenium driver for fast execution
- Target: 100 unit tests, 90%+ coverage

### Integration Tests
- Test complete scrape workflow
- Use real Zillow page snapshots (saved HTML)
- Validate data extraction accuracy

### Performance Tests
- Benchmark each epic's time savings
- Compare against baseline (current implementation)
- Track performance metrics over time

### Regression Tests
- Compare extracted data with baseline
- Test on 50 diverse property types
- Ensure 99%+ data match rate

---

## Monitoring and Metrics

### Key Metrics to Track
1. **Execution Time:** Mean, median, P95, P99
2. **Success Rate:** % successful scrapes
3. **Data Completeness:** % fields extracted per scrape
4. **Image Count:** Average images per property
5. **Error Types:** Categorized error frequency

### Dashboard Requirements
- Real-time performance monitoring
- Historical trend analysis
- Error rate alerts
- Comparative analysis (before/after)

---

## Documentation Requirements

### Code Documentation
- Docstrings for all functions
- Type hints for all parameters
- Inline comments for complex logic
- Performance notes for optimized sections

### User Documentation
- Updated README with performance benchmarks
- Configuration guide for optimization settings
- Troubleshooting guide
- Performance tuning guide

---

## Estimated Total Time Savings

| Epic | Time Savings | Confidence |
|------|--------------|------------|
| Epic 1: Intelligent Wait Strategy | 40-50s | High |
| Epic 2: Streamlined Scrolling | 25-35s | High |
| Epic 3: Optimized Element Discovery | 8-12s | Medium |
| Epic 4: Concurrent Operations | 10-15s | Medium |
| Epic 5: Smart Browser Management | 5-10s | Medium |
| **Total** | **88-122s reduction** | **High** |

**Current:** 60-90 seconds
**Optimized:** 10-20 seconds
**Improvement:** 70-85% faster

---

## Next Steps

1. **Review and approve this plan** with stakeholders
2. **Set up development environment** with testing framework
3. **Create baseline performance metrics** (10 sample scrapes)
4. **Begin Phase 1 implementation** (Epic 1 & 2)
5. **Set up CI/CD pipeline** with performance tests

---

**Plan Status:** ✅ Ready for Implementation
**Last Updated:** 2025-11-07
**Owner:** Diego
