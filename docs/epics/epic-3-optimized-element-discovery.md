# Epic 3: Optimized Element Discovery

**Epic ID:** EPIC-3
**Priority:** P1 (High)
**Status:** Planning
**Owner:** Diego
**Created:** 2025-11-07

---

## Overview

Replace sequential selector attempts with intelligent discovery mechanisms that try most successful selectors first, test multiple selectors in parallel, and optimize XPath usage.

---

## Business Value

**Problem:** Current implementation tries 15+ selectors sequentially for each element type (see all button, gallery container, images), wasting 8-12 seconds per scrape on failed lookups.

**Solution:** Implement selector priority queue based on success history, parallel selector testing via JavaScript, and optimized XPath/CSS selector usage.

**Impact:**
- **Time Savings:** 8-12 seconds per scrape
- **Reliability:** Faster element discovery = fewer timeout failures
- **Adaptability:** Self-learning system adapts to selector changes

---

## Goals

1. Order selectors by success probability
2. Implement parallel selector testing via JavaScript
3. Replace XPath with faster CSS selectors where possible
4. Track selector success rates for continuous improvement
5. Reduce element discovery time by 70%

---

## Success Metrics

- **Performance:** Element discovery < 3 seconds (vs 8-12s currently)
- **Success Rate:** First-try selector success > 80%
- **Efficiency:** Average 2 selector attempts (vs 10+ currently)
- **Adaptability:** Success rate improves over time with learning

---

## Technical Scope

### In Scope
- Selector priority configuration file
- Success rate tracking and learning
- Parallel selector testing via JavaScript
- XPath to CSS selector conversion
- Selector performance benchmarking

### Out of Scope
- Dynamic DOM analysis (too complex for ROI)
- Machine learning selector prediction
- Visual element recognition

---

## Stories

1. **Story 3.1:** Selector Priority Queue - 3-5s savings
2. **Story 3.2:** Parallel Selector Testing - 3-5s savings
3. **Story 3.3:** XPath Optimization - 2-3s savings

**Total Epic Time Savings:** 8-12 seconds

---

## Dependencies

**Upstream:**
- None (can start immediately)

**Downstream:**
- Story 6.1 (Retry Logic) will use selector fallback mechanisms
- Epic 2 benefits from faster gallery container discovery

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Zillow changes selectors frequently | Medium | Medium | Learning system adapts automatically; maintain comprehensive fallback list |
| Parallel testing adds complexity | Low | Low | Implement simple JS loop first, optimize later if needed |
| Success tracking file corruption | Low | Medium | Implement file validation and auto-recovery |
| CSS selectors less specific than XPath | Low | Low | Keep XPath fallbacks for complex selections |

---

## Technical Review Notes

**Story 3.2 (Parallel Testing) - Minor Issue:**

Initial plan showed sequential loop in JS (still not parallel). Revised to true parallel approach:

```javascript
// ❌ Original (still sequential)
for (let selector of selectors) {
    const element = document.querySelector(selector);
    if (element) return [selector, element.textContent];
}

// ✅ Revised (truly parallel via map)
const results = selectors.map(sel =>
    [sel, document.querySelector(sel)]
).find(([sel, el]) => el !== null);
return results || [null, null];
```

**Impact:** No change to time savings estimate (still 3-5s)

---

## Testing Requirements

### Unit Tests
- Test selector priority sorting
- Test success rate tracking
- Test parallel selector logic
- Test XPath to CSS conversion
- Mock success/failure scenarios

### Integration Tests
- Test on 10 different property pages
- Verify element discovery accuracy
- Test fallback behavior
- Validate success tracking persistence

### Performance Tests
- Benchmark selector discovery time
- Compare XPath vs CSS performance
- Measure first-try success rate
- Track improvement over time

---

## Acceptance Criteria

- [ ] Selector configuration file created
- [ ] Priority queue implemented
- [ ] Success tracking working
- [ ] Parallel testing via JS implemented
- [ ] XPath to CSS conversions completed
- [ ] Element discovery < 3 seconds
- [ ] First-try success > 80%
- [ ] Performance tests pass
- [ ] Documentation updated

---

## Implementation Notes

**Current State Analysis:**

Lines with sequential selector attempts:
- Lines 98-110: 11 selectors for "See all" button
- Lines 138-149: 10 selectors for navigation buttons
- Lines 178-187: 8 selectors for gallery container
- Lines 339-355: 15 selectors for images

**Total:** 44 selector attempts per scrape, most failing

**Selector Priority Configuration (selector_config.json):**
```json
{
  "see_all_button": {
    "selectors": [
      {"selector": "button[data-testid='media-stream-see-all']", "priority": 100, "type": "css"},
      {"selector": "button[data-testid='see-all-photos']", "priority": 90, "type": "css"},
      {"selector": "//button[contains(text(), 'See all')]", "priority": 50, "type": "xpath"}
    ]
  },
  "gallery_container": {
    "selectors": [
      {"selector": "ul.hollywood-vertical-media-wall-container", "priority": 100, "type": "css"},
      {"selector": "[data-testid='hollywood-vertical-media-wall']", "priority": 80, "type": "css"}
    ]
  }
}
```

**Success Tracking (selector_stats.json):**
```json
{
  "see_all_button": {
    "button[data-testid='media-stream-see-all']": {"attempts": 150, "successes": 142, "rate": 0.947}
  }
}
```

---

## Related Documentation

- index.py:98-110 - See all button selectors
- index.py:178-187 - Gallery container selectors
- index.py:339-355 - Image selectors
- [CSS Selectors Performance](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
- [Selenium Selector Strategies](https://selenium-python.readthedocs.io/locating-elements.html)

---

**Epic Status:** ✅ Ready for Story Breakdown
**Next Action:** Review Story 3.1 for implementation
**Priority:** Phase 2 (after Epic 1 & 2 quick wins)
