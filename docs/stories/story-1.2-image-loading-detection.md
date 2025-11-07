# Story 1.2: Implement Image Loading Detection

**Story ID:** STORY-1.2
**Epic:** [EPIC-1: Intelligent Wait Strategy](../epics/epic-1-intelligent-wait-strategy.md)
**Priority:** P0 (Critical)
**Status:** Draft
**Points:** 3
**Owner:** Unassigned
**Created:** 2025-11-07

---

## User Story

**As a** scraper
**I want** to detect when images have finished loading
**So that** I don't wait longer than necessary

---

## Business Value

Save 5-10 seconds per scrape by detecting actual image load completion instead of waiting arbitrary amounts of time and hoping all images are loaded.

---

## Acceptance Criteria

### AC1: JavaScript-Based Image Load Detection
- [ ] Implement JS function to check all images loaded
- [ ] Function checks `img.complete` and `img.naturalHeight > 0`
- [ ] Handles lazy-loaded images (checks data-src attributes)
- [ ] Returns true only when ALL images fully loaded

### AC2: Lazy-Load Detection Mechanism
- [ ] Detect images with `loading="lazy"` attribute
- [ ] Detect images with `data-src` attributes
- [ ] Verify lazy images have actual src (not placeholder)
- [ ] Wait for lazy-load mechanism to populate src

### AC3: Batch Image Load Verification
- [ ] Check all images in gallery container
- [ ] Filter out placeholder/icon images
- [ ] Verify minimum image count (e.g., 5 property images)
- [ ] Return count of successfully loaded images

### AC4: Timeout and Fallback
- [ ] Maximum wait time: 3 seconds for all images
- [ ] Fallback to currently visible images on timeout
- [ ] Log timeout with image count at timeout
- [ ] Continue execution with partial image set

### AC5: Integration with Wait Conditions
- [ ] Create custom `EC` condition using image detection
- [ ] Integrate with `WebDriverWait`
- [ ] Use in scrolling operations (Story 2.x)
- [ ] Replace hard-coded waits in lines 300-331

---

## Technical Specification

### JavaScript Image Detection

**⚠️ TECHNICAL REVIEW NOTE:**
The initial approach `img.complete && img.naturalHeight !== 0` doesn't work well for lazy-loaded images. Revised implementation below accounts for lazy-load mechanisms.

```python
def wait_for_images_loaded(driver, container=None, timeout=3):
    """
    Wait for all images to load using JavaScript

    Args:
        driver: Selenium WebDriver instance
        container: Optional WebElement to check images within
        timeout: Maximum seconds to wait

    Returns:
        bool: True if images loaded, False if timeout
    """
    script = """
    const container = arguments[0] || document;

    // Find all images (including lazy-loaded)
    const images = Array.from(container.querySelectorAll('img'));

    // Check if image is properly loaded
    function isImageLoaded(img) {
        // Skip placeholder images
        if (!img.src || img.src.includes('placeholder') || img.src.includes('data:image')) {
            return true;  // Skip these
        }

        // Check if lazy image has real src
        if (img.dataset.src && img.src === img.dataset.placeholder) {
            return false;  // Lazy image not triggered yet
        }

        // Check actual load status
        return img.complete && img.naturalHeight > 0;
    }

    // Filter to property images only (exclude icons, logos, etc.)
    const propertyImages = images.filter(img =>
        img.src && img.src.includes('photos.zillowstatic.com')
    );

    // Check if all property images loaded
    const allLoaded = propertyImages.every(isImageLoaded);
    const loadedCount = propertyImages.filter(isImageLoaded).length;

    return {
        allLoaded: allLoaded,
        totalImages: propertyImages.length,
        loadedImages: loadedCount
    };
    """

    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = driver.execute_script(script, container)

            if result['allLoaded'] and result['totalImages'] > 0:
                print(f"✓ All {result['totalImages']} images loaded")
                return True

            if result['loadedImages'] > 0:
                print(f"Loading: {result['loadedImages']}/{result['totalImages']} images...")

            time.sleep(0.5)  # Check every 500ms

        # Timeout reached
        result = driver.execute_script(script, container)
        print(f"⏱ Timeout: {result['loadedImages']}/{result['totalImages']} images loaded")
        return False

    except Exception as e:
        print(f"Error checking image load: {e}")
        return False
```

### Lazy-Load Trigger Helper

```python
def trigger_lazy_load_images(driver, container=None):
    """
    Force lazy-loaded images to start loading

    Returns:
        int: Number of lazy images triggered
    """
    script = """
    const container = arguments[0] || document;
    const lazyImages = container.querySelectorAll('img[loading="lazy"], img[data-src]');

    let triggered = 0;
    lazyImages.forEach(img => {
        // Set src from data-src if present
        if (img.dataset.src && img.src !== img.dataset.src) {
            img.src = img.dataset.src;
            triggered++;
        }

        // Scroll into view to trigger IntersectionObserver
        img.scrollIntoView({block: 'center', behavior: 'instant'});
    });

    return triggered;
    """

    try:
        count = driver.execute_script(script, container)
        print(f"Triggered {count} lazy-loaded images")
        return count
    except Exception as e:
        print(f"Error triggering lazy load: {e}")
        return 0
```

### Custom Wait Condition

```python
class wait_for_images_in_container:
    """Custom expected condition for image loading"""

    def __init__(self, container_locator, min_images=5):
        self.container_locator = container_locator
        self.min_images = min_images

    def __call__(self, driver):
        """
        Returns container element when images loaded, else False

        Args:
            driver: Selenium WebDriver

        Returns:
            WebElement or False
        """
        try:
            container = driver.find_element(*self.container_locator)

            # Check if images loaded
            script = """
            const container = arguments[0];
            const images = Array.from(container.querySelectorAll('img'));
            const propertyImages = images.filter(img =>
                img.src && img.src.includes('photos.zillowstatic.com') &&
                img.complete && img.naturalHeight > 0
            );
            return propertyImages.length;
            """

            loaded_count = driver.execute_script(script, container)

            if loaded_count >= self.min_images:
                return container
            else:
                return False

        except:
            return False

# Usage
try:
    container = WebDriverWait(driver, 5).until(
        wait_for_images_in_container(
            (By.CSS_SELECTOR, ".hollywood-vertical-media-wall-container"),
            min_images=5
        )
    )
    print(f"Gallery loaded with images")
except TimeoutException:
    print("Gallery loaded but images still loading, continuing...")
```

---

## Implementation Checklist

### Phase 1: Basic Image Detection
- [ ] Implement `wait_for_images_loaded()` function
- [ ] Add JavaScript image check logic
- [ ] Handle lazy-loaded images
- [ ] Test on single property

### Phase 2: Lazy-Load Support
- [ ] Implement `trigger_lazy_load_images()` function
- [ ] Test lazy-load triggering
- [ ] Verify src population

### Phase 3: Custom Wait Condition
- [ ] Create `wait_for_images_in_container` class
- [ ] Integrate with `WebDriverWait`
- [ ] Test with various container selectors

### Phase 4: Integration
- [ ] Replace waits in lines 300-331
- [ ] Use after gallery expansion
- [ ] Use after scrolling operations
- [ ] Add timeout handling

### Phase 5: Testing
- [ ] Unit tests for JS functions
- [ ] Integration tests on 5+ properties
- [ ] Performance benchmarks

---

## Testing Requirements

### Unit Tests

```python
def test_image_detection_script():
    """Test JS image detection logic"""
    # Create mock page with loaded/unloaded images
    # Verify script returns correct status

def test_lazy_load_trigger():
    """Test lazy image triggering"""
    # Create mock page with lazy images
    # Verify src updated after trigger

def test_custom_wait_condition():
    """Test custom EC for image loading"""
    # Mock driver with container
    # Verify condition returns container when loaded
```

### Integration Tests

```python
def test_image_loading_on_live_page():
    """Test image detection on real Zillow page"""
    driver.get(ZILLOW_URL)
    # Click see all
    # Wait for images using new detection
    # Verify images actually loaded
    # Compare time to arbitrary wait

def test_timeout_handling():
    """Test fallback on slow image loading"""
    # Throttle network
    # Verify timeout triggers
    # Verify partial images returned
```

### Performance Tests

```python
def test_wait_time_improvement():
    """Benchmark image wait time"""
    # Test on 5 properties
    # Measure wait time for images
    # Verify 5-10s savings
    # Verify no images missed
```

---

## Dependencies

**Requires:**
- Story 1.1 (Explicit Wait Conditions) - provides wait infrastructure

**Blocks:**
- Story 2.3 (Progressive Discovery) - uses image detection
- Story 2.1 (Unified Scroll) - uses image loading detection

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Lazy-load mechanism doesn't trigger | High | Medium | Fallback to scrolling; test multiple trigger methods |
| Image detection too slow | Medium | Low | Optimize JS; check every 500ms max |
| False positives (placeholders detected as loaded) | Medium | Low | Filter placeholder images; check naturalHeight |

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Image detection functions implemented
- [ ] Lazy-load support working
- [ ] Custom wait condition integrated
- [ ] Unit tests passing (100% coverage)
- [ ] Integration tests passing on 5+ properties
- [ ] Performance benchmark shows 5-10s savings
- [ ] No missed images vs baseline
- [ ] Code review completed
- [ ] Documentation updated

---

## Estimated Time Savings

**Current:** 8-13 seconds of arbitrary waits for images
**Optimized:** 1-3 seconds of detection-based waits
**Savings:** 5-10 seconds per scrape

---

## Related Files

- `index.py` lines 300-331 - Image loading waits to replace
- `index.py` lines 333-416 - Image extraction logic

---

**Story Status:** ✅ Ready for Implementation
**Next Action:** Requires Story 1.1 completion first
