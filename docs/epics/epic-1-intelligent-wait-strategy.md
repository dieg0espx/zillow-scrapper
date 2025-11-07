# Epic 1: Intelligent Wait Strategy

**Epic ID:** EPIC-1
**Priority:** P0 (Critical)
**Status:** Planning
**Owner:** Diego
**Created:** 2025-11-07

---

## Overview

Replace hard-coded `time.sleep()` calls with intelligent, event-driven wait mechanisms that only wait as long as necessary for elements and images to load.

---

## Business Value

**Problem:** Current implementation wastes 50+ seconds waiting with arbitrary sleep timers that either wait too long (wasting time) or too short (causing failures).

**Solution:** Implement Selenium's explicit waits with custom conditions that detect actual page state changes.

**Impact:**
- **Time Savings:** 35-45 seconds per scrape (58% of total waste)
- **Reliability:** Reduces timeout-related failures
- **Adaptability:** Automatically adjusts to varying network conditions

---

## Goals

1. Eliminate all unnecessary `time.sleep()` calls
2. Implement explicit wait conditions for all operations
3. Create custom wait conditions for image loading
4. Add dynamic wait time calculation based on network performance
5. Maintain or improve success rate

---

## Success Metrics

- **Performance:** Reduce wait time from 50-80s to 5-10s
- **Reliability:** ≤ 1% timeout failures
- **Code Quality:** Zero hard-coded sleep calls in final implementation
- **Validation:** 100% data match with current implementation

---

## Technical Scope

### In Scope
- Replace all `time.sleep()` with `WebDriverWait`
- Implement custom wait conditions for lazy-loaded images
- Add timeout handling with graceful fallbacks
- Network performance measurement
- Dynamic wait multiplier calculation

### Out of Scope
- Browser performance optimization (covered in Epic 5)
- Element discovery optimization (covered in Epic 3)
- Retry logic (covered in Epic 6)

---

## Stories

1. **Story 1.1:** Implement Explicit Wait Conditions - 30-40s savings
2. **Story 1.2:** Implement Image Loading Detection - 5-10s savings
3. **Story 1.3:** Dynamic Wait Time Calculation - 2-5s savings

**Total Epic Time Savings:** 35-45 seconds

---

## Dependencies

**Upstream:**
- None (can start immediately)

**Downstream:**
- Epic 2 (Streamlined Scrolling) depends on wait conditions from Story 1.2
- Epic 6 (Error Handling) will leverage timeout handling

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Zillow dynamic content delays | Medium | Medium | Implement generous max timeouts (10s) with exponential backoff |
| Network variability causes flaky tests | Medium | Low | Story 1.3 adds adaptive waits based on measured performance |
| Custom conditions too aggressive | Low | Medium | Add fallback logic to revert to longer waits on failures |

---

## Testing Requirements

### Unit Tests
- Test each wait condition in isolation
- Mock Selenium driver states (element loaded, not loaded, timeout)
- Verify timeout handling and fallbacks

### Integration Tests
- Test on live Zillow pages (5 different properties)
- Validate data extraction accuracy matches baseline
- Measure actual time savings

### Performance Tests
- Benchmark wait times before/after
- Test under varying network conditions (fast, slow, intermittent)
- Verify no increase in timeout failures

---

## Acceptance Criteria

- [ ] All `time.sleep()` calls removed from codebase
- [ ] Custom wait conditions implemented and tested
- [ ] Timeout handling with fallbacks in place
- [ ] Performance tests show 35-45s time savings
- [ ] Data accuracy ≥ 99% vs baseline
- [ ] Zero increase in failure rate
- [ ] Code review completed
- [ ] Documentation updated

---

## Implementation Notes

**Current State Analysis:**
- 15+ `time.sleep()` calls throughout index.py
- Lines with sleep: 122, 130, 161, 171, 203, 216, 226, 244, 258, 264, 283, 294, 301, 316, 322, 331
- Total sleep time: 50-80 seconds per execution
- No use of custom wait conditions

**Key Implementation Areas:**
1. Gallery expansion waits (lines 122, 130, 161, 171)
2. Scrolling operation waits (lines 203-331)
3. Image loading waits (lines 300-331)
4. Navigation waits (lines 258, 316)

---

## Related Documentation

- [Selenium Explicit Waits Documentation](https://selenium-python.readthedocs.io/waits.html)
- [Custom Expected Conditions](https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.support.expected_conditions)
- index.py:38-39 - Already uses WebDriverWait for initial elements

---

**Epic Status:** ✅ Ready for Story Breakdown
**Next Action:** Review and approve Story 1.1 for implementation
