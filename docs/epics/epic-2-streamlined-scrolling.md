# Epic 2: Streamlined Scrolling Strategy

**Epic ID:** EPIC-2
**Priority:** P0 (Critical)
**Status:** Planning
**Owner:** Diego
**Created:** 2025-11-07

---

## Overview

Consolidate 4 redundant scrolling strategies into a single intelligent algorithm that discovers images progressively and exits early when all images are found.

---

## Business Value

**Problem:** Current implementation executes 4 separate scrolling strategies sequentially (main page scroll, gallery scroll, item-by-item scroll, final comprehensive scroll), causing massive time waste and redundant operations.

**Solution:** Single adaptive scrolling algorithm that targets the media wall container directly, discovers images progressively, and exits early when count stabilizes.

**Impact:**
- **Time Savings:** 15-25 seconds per scrape (major bottleneck elimination)
- **Efficiency:** 75% reduction in scroll operations
- **Reliability:** Fewer opportunities for scroll-related failures

---

## Goals

1. Remove 4 redundant scrolling strategies
2. Implement single unified scroll algorithm
3. Enable progressive image discovery with early exit
4. Research and implement lazy-load triggering mechanism
5. Reduce total scrolling time to < 5 seconds

---

## Success Metrics

- **Performance:** Scrolling completes in < 5 seconds (vs 40-50s currently)
- **Image Discovery:** 100% of available images extracted
- **Efficiency:** Max 5 scroll iterations (vs 30+ currently)
- **Reliability:** Zero scroll-related failures

---

## Technical Scope

### In Scope
- Unified scroll algorithm targeting media wall container
- Progressive image URL discovery during scrolling
- Early exit logic when image count stabilizes
- JavaScript-based lazy-load triggering (research required)
- Fallback scrolling if lazy-load trigger fails

### Out of Scope
- Image filtering optimization (covered in Epic 4)
- Wait time optimization (covered in Epic 1)
- Selector optimization (covered in Epic 3)

---

## Stories

1. **Story 2.1:** Unified Scroll Algorithm - 10-15s savings
2. **Story 2.2:** JavaScript-Based Lazy Load Trigger - 5-10s savings (HIGH RISK - needs R&D)
3. **Story 2.3:** Progressive Image Discovery - 5-10s savings

**Total Epic Time Savings:** 15-25 seconds (revised from 25-35s)

---

## Dependencies

**Upstream:**
- Story 1.2 (Image Loading Detection) - provides wait conditions for images

**Downstream:**
- Story 4.1 (Parallel Data Extraction) can extract images while scrolling
- Story 6.2 (Graceful Degradation) handles partial image extraction

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| JS lazy-load trigger doesn't work with Zillow's IntersectionObserver | **HIGH** | High | Story 2.2 includes fallback to minimal scrolling |
| Image count never stabilizes | Medium | Medium | Set maximum iteration cap (5 scrolls) |
| Early exit misses some images | Low | High | Require 2 consecutive stable counts before exit |
| Zillow changes media wall structure | Medium | Medium | Multiple fallback selectors + monitoring |

---

## ⚠️ Technical Review Notes

**Story 2.2 (Lazy Load Trigger) - HIGH RISK:**

The initial plan assumed we could trigger lazy-loads via JavaScript by setting `img.src = img.dataset.src`. However, Zillow likely uses `IntersectionObserver` with server-side validation, which means:

1. Images require viewport visibility to load
2. Simply setting `src` may not trigger the observer
3. May need server authentication tokens

**Revised Approach:**
- Phase 1: Implement Story 2.2 as R&D/POC
- Test if JS trigger works on live Zillow page
- If fails, fall back to optimized scrolling (Story 2.1 + 2.3)
- Document findings for future optimization

**Impact on Timeline:**
- Story 2.2 may take 2-3x longer than estimated
- May need to deprioritize if R&D shows it's not viable
- Stories 2.1 and 2.3 are low-risk and deliver 15-20s savings

---

## Testing Requirements

### Unit Tests
- Test scroll position calculation logic
- Test image discovery and deduplication
- Test early exit conditions
- Mock media wall container

### Integration Tests
- Test on 10 different property types
- Verify all images extracted vs baseline
- Test scroll fallback when gallery not found
- Validate early exit triggers correctly

### Performance Tests
- Benchmark scrolling time before/after
- Measure scroll iterations (target: ≤ 5)
- Verify image discovery completeness
- Test under slow network conditions

### Research Tests (Story 2.2)
- Test JS lazy-load trigger on live Zillow
- Document IntersectionObserver behavior
- Measure time savings if successful
- Implement fallback if unsuccessful

---

## Acceptance Criteria

- [ ] All 4 redundant strategies removed
- [ ] Single scroll algorithm implemented
- [ ] Media wall container targeted directly
- [ ] Progressive discovery with early exit working
- [ ] Lazy-load trigger researched and attempted
- [ ] Fallback scrolling implemented
- [ ] Scrolling completes in < 5 seconds
- [ ] 100% image discovery maintained
- [ ] Performance tests pass
- [ ] Documentation updated

---

## Implementation Notes

**Current State Analysis:**
```
Strategy 1 (lines 208-216): Main page scroll, 5 stops, 10s
Strategy 2 (lines 218-226): Gallery scroll, 5 stops, 10s
Strategy 2.5 (lines 228-248): Item-by-item scroll, variable, 10-30s
Strategy 3 (lines 250-266): Click through images, 20 iterations, 10s
Strategy 4 (lines 268-283): Final comprehensive scroll, 5 stops, 7.5s

Total: 47.5-67.5 seconds of scrolling
```

**Unified Algorithm Approach:**
1. Find media wall container once
2. Calculate scroll height
3. Scroll 3-5 positions within container only
4. Extract images after each scroll
5. Exit if count stable for 2 iterations
6. Max 5 iterations regardless

**Expected Result:** 3-5 seconds total

---

## Related Documentation

- index.py:173-297 - Current scrolling implementation
- [IntersectionObserver API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)
- [Selenium JavaScript Execution](https://selenium-python.readthedocs.io/api.html#selenium.webdriver.remote.webdriver.WebDriver.execute_script)

---

**Epic Status:** ✅ Ready for Story Breakdown
**Next Action:** Review Story 2.1 (Unified Scroll) for immediate implementation
**Research Required:** Story 2.2 (Lazy Load Trigger) - proceed with caution
