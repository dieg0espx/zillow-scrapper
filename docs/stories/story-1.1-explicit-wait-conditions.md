# Story 1.1: Implement Explicit Wait Conditions

**Story ID:** STORY-1.1
**Epic:** [EPIC-1: Intelligent Wait Strategy](../epics/epic-1-intelligent-wait-strategy.md)
**Priority:** P0 (Critical)
**Status:** Draft
**Points:** 5
**Owner:** Unassigned
**Created:** 2025-11-07

---

## User Story

**As a** developer
**I want** to use Selenium's explicit waits with proper conditions
**So that** the scraper only waits as long as necessary for elements to load

---

## Business Value

Eliminate 30-40 seconds of unnecessary waiting per scrape by replacing arbitrary `time.sleep()` calls with intelligent wait conditions that detect actual page state changes.

---

## Acceptance Criteria

### AC1: Replace All time.sleep() Calls
- [ ] All `time.sleep()` calls removed from index.py
- [ ] Each replaced with appropriate `WebDriverWait` + condition
- [ ] Zero hard-coded sleep calls remain

**Lines to update:** 122, 130, 161, 171, 203, 216, 226, 244, 258, 264, 283, 294, 301, 316, 322, 331

### AC2: Implement Standard Wait Conditions
- [ ] `EC.presence_of_element_located()` for element existence
- [ ] `EC.visibility_of_element_located()` for visible elements
- [ ] `EC.element_to_be_clickable()` for clickable buttons
- [ ] Maximum wait time: 10 seconds per operation
- [ ] Timeout handling with meaningful error messages

### AC3: Create Custom Wait Conditions
- [ ] Custom condition for image src attribute population
- [ ] Custom condition for gallery container loaded
- [ ] Custom condition for minimum image count
- [ ] All custom conditions documented with docstrings

### AC4: Implement Exponential Backoff
- [ ] Failed waits retry with backoff: 100ms, 200ms, 500ms
- [ ] Maximum 3 retry attempts per operation
- [ ] Log all retry attempts
- [ ] Fallback behavior on final failure

### AC5: Add Timeout Handling
- [ ] Graceful handling of `TimeoutException`
- [ ] Log timeout location and element selector
- [ ] Continue execution with partial data when possible
- [ ] Re-raise exception only for critical failures

---

## Technical Specification

### Current State

**Lines 122, 130:** Wait after "See all" button click
```python
elements[0].click()
see_all_clicked = True
print("Clicked 'See all' button")
time.sleep(3)  # ❌ Hard-coded 3 second wait
```

**Lines 203-331:** Scrolling wait times
- 15+ `time.sleep()` calls ranging from 0.5s to 3s
- Total: ~50 seconds of waiting

### Target State

**Replace with explicit waits:**
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Standard wait after button click
elements[0].click()
see_all_clicked = True
print("Clicked 'See all' button")

# Wait for gallery to appear instead of arbitrary sleep
try:
    gallery = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".hollywood-vertical-media-wall-container"))
    )
    print("Gallery loaded")
except TimeoutException:
    print("Gallery not found, continuing with fallback")
```

### Custom Wait Conditions

```python
class CustomConditions:
    """Custom wait conditions for Zillow scraper"""

    @staticmethod
    def images_loaded_in_container(container_locator, min_images=5):
        """Wait for minimum number of images to load in container"""
        def _predicate(driver):
            try:
                container = driver.find_element(*container_locator)
                images = container.find_elements(By.TAG_NAME, "img")
                loaded_images = [img for img in images if img.get_attribute('src') and 'http' in img.get_attribute('src')]
                return len(loaded_images) >= min_images
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
                return src and 'http' in src and 'placeholder' not in src
            except:
                return False
        return _predicate

    @staticmethod
    def image_count_stable(container_locator, stability_checks=2):
        """Wait for image count to stabilize (no new images loading)"""
        counts = []
        def _predicate(driver):
            try:
                container = driver.find_element(*container_locator)
                images = container.find_elements(By.TAG_NAME, "img")
                current_count = len([img for img in images if img.get_attribute('src')])
                counts.append(current_count)

                # Need at least 2 checks to compare
                if len(counts) < stability_checks:
                    return False

                # Check if last N counts are the same
                return len(set(counts[-stability_checks:])) == 1
            except:
                return False
        return _predicate
```

### Exponential Backoff Implementation

```python
def wait_with_backoff(driver, condition, max_wait=10, backoff_delays=[0.1, 0.2, 0.5]):
    """Wait with exponential backoff retry"""
    for attempt, delay in enumerate(backoff_delays):
        try:
            return WebDriverWait(driver, max_wait).until(condition)
        except TimeoutException:
            if attempt < len(backoff_delays) - 1:
                print(f"Wait attempt {attempt+1} failed, retrying in {delay}s...")
                time.sleep(delay)
            else:
                # Final attempt failed
                raise
    return None
```

---

## Implementation Checklist

### Phase 1: Replace Gallery Expansion Waits
- [ ] Line 122: Replace sleep after "See all" click
- [ ] Line 130: Replace sleep after "See all" click (alternate path)
- [ ] Line 161: Replace sleep after nav button click
- [ ] Line 171: Replace sleep after gallery wait

### Phase 2: Replace Scrolling Waits
- [ ] Lines 203, 216, 226: Replace scrolling waits
- [ ] Lines 244, 258, 264: Replace item scroll waits
- [ ] Lines 283, 294: Replace comprehensive scroll waits
- [ ] Lines 301, 316, 322, 331: Replace final wait times

### Phase 3: Add Custom Conditions
- [ ] Implement `CustomConditions` class
- [ ] Add `images_loaded_in_container` condition
- [ ] Add `element_has_valid_src` condition
- [ ] Add `image_count_stable` condition

### Phase 4: Add Backoff Logic
- [ ] Implement `wait_with_backoff` function
- [ ] Apply to critical wait operations
- [ ] Add retry logging

### Phase 5: Error Handling
- [ ] Wrap all waits in try/except
- [ ] Log timeout exceptions
- [ ] Implement graceful fallbacks
- [ ] Test timeout scenarios

---

## Testing Requirements

### Unit Tests

```python
def test_custom_condition_images_loaded():
    """Test custom condition for images loaded"""
    # Mock driver and container with images
    # Verify condition returns True when min_images met

def test_wait_with_backoff_success():
    """Test backoff succeeds on retry"""
    # Mock condition that fails twice then succeeds
    # Verify backoff delays applied correctly

def test_wait_with_backoff_timeout():
    """Test backoff raises TimeoutException after all retries"""
    # Mock condition that always fails
    # Verify exception raised after final attempt
```

### Integration Tests

```python
def test_gallery_wait_replaces_sleep():
    """Test gallery appears without arbitrary sleep"""
    # Click "See all" button
    # Verify gallery loads within 5 seconds
    # Compare time to baseline (should be faster)

def test_timeout_handling():
    """Test graceful handling of element not found"""
    # Navigate to page missing expected element
    # Verify timeout logged
    # Verify execution continues with partial data
```

### Performance Tests

```python
def test_wait_time_reduction():
    """Benchmark total wait time before/after"""
    # Run scraper on 5 properties
    # Measure total execution time
    # Verify 30-40s reduction
    # Verify data accuracy maintained
```

---

## Dependencies

**Requires:**
- None (can start immediately)

**Blocks:**
- Story 1.2 (Image Loading Detection) - uses custom conditions
- Story 2.1 (Unified Scroll Algorithm) - uses wait conditions
- All other stories benefit from wait infrastructure

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Waits too short cause failures | High | Medium | Set generous default timeouts (10s); monitor failure rates |
| Custom conditions too complex | Medium | Low | Keep conditions simple; comprehensive testing |
| Zillow dynamic loading delays | Medium | Medium | Use backoff retry; fallback to longer waits |

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All `time.sleep()` calls removed
- [ ] Custom wait conditions implemented and tested
- [ ] Unit tests written and passing (100% coverage)
- [ ] Integration tests passing on 5+ properties
- [ ] Performance benchmark shows 30-40s savings
- [ ] Data accuracy ≥ 99% vs baseline
- [ ] Code review completed
- [ ] Documentation updated (docstrings, README)
- [ ] No increase in error rate

---

## Estimated Time Savings

**Current:** 50-80 seconds of hard-coded waits
**Optimized:** 5-10 seconds of intelligent waits
**Savings:** 30-40 seconds per scrape

---

## Related Files

- `index.py` lines 122, 130, 161, 171, 203-331 - Sleep calls to replace
- `index.py` line 39 - Existing WebDriverWait usage (reference)

---

**Story Status:** ✅ Ready for Implementation
**Next Action:** Assign to developer and begin Phase 1
