# Story 2.1: Unified Scroll Algorithm

**Story ID:** STORY-2.1
**Epic:** [EPIC-2: Streamlined Scrolling Strategy](../epics/epic-2-streamlined-scrolling.md)
**Priority:** P0 (Critical)
**Status:** Draft
**Points:** 5
**Owner:** Unassigned
**Created:** 2025-11-07

---

## User Story

**As a** developer
**I want** a single intelligent scrolling strategy
**So that** I eliminate redundant scrolling operations

---

## Business Value

Save 10-15 seconds per scrape by consolidating 4 redundant scrolling strategies into one optimized algorithm that targets the media wall directly.

---

## Acceptance Criteria

### AC1: Remove Redundant Strategies
- [ ] Remove Strategy 1 (lines 208-216): Main page scroll
- [ ] Remove Strategy 2 (lines 218-226): Gallery scroll
- [ ] Remove Strategy 2.5 (lines 228-248): Item-by-item scroll
- [ ] Remove Strategy 3 (lines 250-266): Click-through navigation
- [ ] Remove Strategy 4 (lines 268-283): Final comprehensive scroll

### AC2: Implement Unified Algorithm
- [ ] Target media wall container directly
- [ ] Calculate optimal scroll positions (3-5 stops max)
- [ ] Scroll ONLY within gallery container (not main page)
- [ ] Wait for images after each scroll stop
- [ ] Complete scrolling in < 5 seconds

### AC3: Viewport-Based Progressive Scrolling
- [ ] Calculate container height
- [ ] Divide into 3-5 scroll positions
- [ ] Scroll to each position smoothly
- [ ] Trigger lazy-load at each stop
- [ ] Exit early if all images loaded (Story 2.3 integration)

### AC4: Fallback Handling
- [ ] Detect if media wall container not found
- [ ] Fall back to main page scrolling
- [ ] Use minimal scroll stops (3 max)
- [ ] Log fallback usage

### AC5: Performance Optimization
- [ ] Use `scrollTop` instead of `scrollIntoView` (faster)
- [ ] Batch scroll operations (no delays between calculations)
- [ ] Maximum 5 scroll iterations regardless of outcome
- [ ] Total scroll time < 5 seconds

---

## Technical Specification

### Current State Problems

**Lines 208-283:** Four separate scrolling strategies
```python
# Strategy 1: Main page scroll (5 stops, ~10s)
for i, position in enumerate(scroll_positions):
    driver.execute_script(f"window.scrollTo(0, {int(position)});")
    time.sleep(2)

# Strategy 2: Gallery scroll (5 stops, ~10s)
for i, position in enumerate(gallery_positions):
    driver.execute_script("arguments[0].scrollTop = arguments[1];", gallery_element, int(position))
    time.sleep(2)

# Strategy 2.5: Item-by-item (variable, 10-30s)
for i, item in enumerate(list_items):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
    time.sleep(1)

# Strategy 3: Click navigation (20 iterations, ~10s)
for i in range(20):
    next_buttons[0].click()
    time.sleep(0.5)

# Strategy 4: Final scroll (5 stops, ~7.5s)
for i in range(5):
    driver.execute_script(f"window.scrollTo(0, {int(final_page_positions[i])});")
    time.sleep(1.5)

# Total: 47.5-67.5 seconds!
```

### Unified Algorithm

```python
def scroll_gallery_unified(driver, gallery_container, max_scrolls=5):
    """
    Unified scrolling algorithm for image gallery

    Args:
        driver: Selenium WebDriver
        gallery_container: WebElement of media wall container
        max_scrolls: Maximum scroll iterations

    Returns:
        int: Number of scroll stops performed
    """
    print("Starting unified scroll algorithm...")

    try:
        # Get gallery dimensions
        gallery_height = driver.execute_script(
            "return arguments[0].scrollHeight;",
            gallery_container
        )
        viewport_height = driver.execute_script(
            "return arguments[0].clientHeight;",
            gallery_container
        )

        # Calculate optimal scroll positions (3-5 stops)
        scrollable_height = gallery_height - viewport_height

        if scrollable_height <= 0:
            print("Gallery fits in viewport, no scrolling needed")
            return 0

        # Calculate stop positions (exclude 0% and 100%, focus on middle)
        num_stops = min(5, max(3, int(scrollable_height / 1000)))  # 1 stop per 1000px
        positions = [scrollable_height * (i + 1) / (num_stops + 1) for i in range(num_stops)]

        print(f"Gallery height: {gallery_height}px, scrollable: {scrollable_height}px")
        print(f"Scrolling to {num_stops} positions...")

        scroll_count = 0
        for i, position in enumerate(positions):
            # Scroll to position
            driver.execute_script(
                "arguments[0].scrollTop = arguments[1];",
                gallery_container,
                int(position)
            )

            scroll_count += 1
            print(f"Scroll stop {i+1}/{num_stops} at {int(position)}px")

            # Wait for images to load at this position (Story 1.2)
            wait_for_images_loaded(driver, gallery_container, timeout=1)

            # Optional: Check if all images loaded (Story 2.3)
            # If yes, exit early

        # Final scroll to bottom
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight;",
            gallery_container
        )
        scroll_count += 1
        print(f"Scrolled to bottom")

        # Wait for final images
        wait_for_images_loaded(driver, gallery_container, timeout=1)

        print(f"✓ Unified scroll complete: {scroll_count} stops")
        return scroll_count

    except Exception as e:
        print(f"Error during unified scroll: {e}")
        return 0
```

### Fallback Strategy

```python
def scroll_with_fallback(driver, max_scrolls=3):
    """
    Fallback scrolling if gallery container not found

    Args:
        driver: Selenium WebDriver
        max_scrolls: Maximum scroll iterations

    Returns:
        int: Number of scroll stops performed
    """
    print("Using fallback scrolling strategy (main page)...")

    try:
        page_height = driver.execute_script("return document.body.scrollHeight;")
        viewport_height = driver.execute_script("return window.innerHeight;")
        scrollable_height = page_height - viewport_height

        if scrollable_height <= 0:
            print("Page fits in viewport, no scrolling needed")
            return 0

        # Minimal scroll stops (3 max)
        positions = [scrollable_height * 0.33, scrollable_height * 0.67, scrollable_height]

        scroll_count = 0
        for i, position in enumerate(positions):
            driver.execute_script(f"window.scrollTo(0, {int(position)});")
            scroll_count += 1
            print(f"Fallback scroll {i+1}/3 at {int(position)}px")

            # Brief wait for lazy load
            time.sleep(0.5)

        print(f"✓ Fallback scroll complete: {scroll_count} stops")
        return scroll_count

    except Exception as e:
        print(f"Error during fallback scroll: {e}")
        return 0
```

### Integration with Existing Code

```python
# Replace lines 173-297 with:
try:
    # Find media wall container
    gallery_element = None
    gallery_selectors = [
        "ul.hollywood-vertical-media-wall-container",
        "[data-testid='hollywood-vertical-media-wall']",
        ".StyledVerticalMediaWall-fshdp-8-111-1__sc-1liu0fm-3"
    ]

    for selector in gallery_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                gallery_element = elements[0]
                print(f"Found gallery container: {selector}")
                break
        except:
            continue

    # Unified scrolling
    if gallery_element:
        scroll_count = scroll_gallery_unified(driver, gallery_element, max_scrolls=5)
    else:
        print("Gallery container not found, using fallback")
        scroll_count = scroll_with_fallback(driver, max_scrolls=3)

    print(f"Total scroll operations: {scroll_count}")

except Exception as e:
    print(f"Error during scrolling: {e}")
```

---

## Implementation Checklist

### Phase 1: Remove Old Code
- [ ] Delete Strategy 1 (lines 208-216)
- [ ] Delete Strategy 2 (lines 218-226)
- [ ] Delete Strategy 2.5 (lines 228-248)
- [ ] Delete Strategy 3 (lines 250-266)
- [ ] Delete Strategy 4 (lines 268-283)

### Phase 2: Implement Unified Algorithm
- [ ] Create `scroll_gallery_unified()` function
- [ ] Add gallery dimension calculation
- [ ] Add optimal position calculation
- [ ] Add scroll execution
- [ ] Add image loading waits

### Phase 3: Add Fallback
- [ ] Create `scroll_with_fallback()` function
- [ ] Add main page scrolling
- [ ] Add minimal scroll logic

### Phase 4: Integration
- [ ] Replace old code with unified approach
- [ ] Add gallery container discovery
- [ ] Add fallback handling
- [ ] Add logging

### Phase 5: Testing
- [ ] Test on properties with many images
- [ ] Test on properties with few images
- [ ] Test fallback when gallery not found
- [ ] Benchmark performance

---

## Testing Requirements

### Unit Tests

```python
def test_scroll_position_calculation():
    """Test optimal scroll position calculation"""
    # Test various gallery heights
    # Verify 3-5 stops calculated correctly

def test_scroll_execution():
    """Test scroll commands"""
    # Mock driver and gallery element
    # Verify scrollTop set correctly

def test_fallback_logic():
    """Test fallback when gallery not found"""
    # Mock driver without gallery
    # Verify fallback scrolling triggered
```

### Integration Tests

```python
def test_unified_scroll_on_live_page():
    """Test on real Zillow page"""
    # Navigate to property page
    # Click see all
    # Execute unified scroll
    # Verify all images discovered
    # Verify time < 5 seconds

def test_scroll_with_few_images():
    """Test on property with few images"""
    # Should complete quickly
    # Should not over-scroll

def test_scroll_with_many_images():
    """Test on property with 50+ images"""
    # Should discover all images
    # Should complete in < 5 seconds
```

### Performance Tests

```python
def test_scroll_time_reduction():
    """Benchmark scroll time"""
    # Test on 10 properties
    # Measure scroll time
    # Verify < 5 seconds per property
    # Verify 30-40s savings vs old approach
```

---

## Dependencies

**Requires:**
- Story 1.2 (Image Loading Detection) - uses `wait_for_images_loaded()`

**Blocks:**
- Story 2.3 (Progressive Discovery) - integrates early exit logic

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Gallery container selector changes | High | Medium | Multiple fallback selectors; fallback to main page |
| Insufficient scroll stops miss images | High | Low | Test with various image counts; increase max_scrolls if needed |
| Scroll too fast for lazy-load | Medium | Low | Wait for images after each stop; adjust timing if needed |

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Old scrolling code removed
- [ ] Unified algorithm implemented
- [ ] Fallback strategy working
- [ ] Unit tests passing
- [ ] Integration tests on 10+ properties
- [ ] Scroll time < 5 seconds
- [ ] 100% image discovery maintained
- [ ] Code review completed
- [ ] Documentation updated

---

## Estimated Time Savings

**Current:** 47.5-67.5 seconds of scrolling (4 strategies)
**Optimized:** 3-5 seconds of unified scrolling
**Savings:** 10-15 seconds per scrape

---

## Related Files

- `index.py` lines 173-297 - Scrolling code to replace
- Story 1.2 implementation - Image loading detection
- Story 2.3 - Will add early exit logic

---

**Story Status:** ✅ Ready for Implementation
**Next Action:** Requires Story 1.2 completion first
