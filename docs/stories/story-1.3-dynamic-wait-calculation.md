# Story 1.3: Dynamic Wait Time Calculation

**Story ID:** STORY-1.3
**Epic:** [EPIC-1: Intelligent Wait Strategy](../epics/epic-1-intelligent-wait-strategy.md)
**Priority:** P1 (High)
**Status:** Draft
**Points:** 2
**Owner:** Unassigned
**Created:** 2025-11-07

---

## User Story

**As a** developer
**I want** to calculate optimal wait times based on network performance
**So that** the scraper adapts to different network conditions

---

## Business Value

Save 2-5 seconds per scrape by adapting wait times to actual network performance rather than using one-size-fits-all timeouts. Improves reliability on slow networks and speed on fast networks.

---

## Acceptance Criteria

### AC1: Measure Page Load Time
- [ ] Record navigation timing on initial page load
- [ ] Calculate page load baseline (DOM complete time)
- [ ] Store baseline in property_data dict
- [ ] Log baseline for monitoring

### AC2: Calculate Dynamic Wait Multipliers
- [ ] Fast network (< 2s load): 0.5x multiplier
- [ ] Normal network (2-5s load): 1.0x multiplier
- [ ] Slow network (> 5s load): 2.0x multiplier
- [ ] Apply multipliers to all subsequent waits

### AC3: Apply Multipliers to Wait Operations
- [ ] Adjust `WebDriverWait` timeout values
- [ ] Adjust custom wait condition timeouts
- [ ] Adjust retry backoff delays
- [ ] Maintain reasonable min/max bounds (1s-20s)

### AC4: Track and Log Performance Metrics
- [ ] Log actual vs expected wait times
- [ ] Track wait success/failure rates
- [ ] Calculate average wait time per scrape
- [ ] Include in performance metrics JSON

### AC5: Provide Performance Report
- [ ] Generate performance summary after scrape
- [ ] Include network baseline, multiplier used
- [ ] Include actual wait times per operation
- [ ] Include recommendations for tuning

---

## Technical Specification

### Navigation Timing API

```python
def measure_page_load_performance(driver):
    """
    Measure page load performance using Navigation Timing API

    Returns:
        dict: Performance metrics
    """
    script = """
    const timing = window.performance.timing;
    const navigation = window.performance.navigation;

    return {
        // Page load times
        domainLookup: timing.domainLookupEnd - timing.domainLookupStart,
        connect: timing.connectEnd - timing.connectStart,
        response: timing.responseEnd - timing.responseStart,
        domProcessing: timing.domComplete - timing.domLoading,
        pageLoad: timing.loadEventEnd - timing.navigationStart,

        // Total time to interactive
        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
        domComplete: timing.domComplete - timing.navigationStart,

        // Network info
        navigationType: navigation.type,
        redirectCount: navigation.redirectCount
    };
    """

    try:
        # Wait for page to fully load
        driver.execute_script("return document.readyState") == "complete"

        perf = driver.execute_script(script)

        # Calculate load time in seconds
        load_time = perf['domComplete'] / 1000.0

        print(f"Page load time: {load_time:.2f}s")
        print(f"  - DNS lookup: {perf['domainLookup']}ms")
        print(f"  - Connection: {perf['connect']}ms")
        print(f"  - Response: {perf['response']}ms")
        print(f"  - DOM processing: {perf['domProcessing']}ms")

        return perf

    except Exception as e:
        print(f"Error measuring performance: {e}")
        return None
```

### Dynamic Wait Multiplier

```python
class DynamicWaitConfig:
    """Configuration for adaptive wait times"""

    def __init__(self, driver):
        self.driver = driver
        self.baseline_load_time = None
        self.multiplier = 1.0
        self.wait_times = []

    def measure_baseline(self, url):
        """
        Measure baseline performance by loading page

        Args:
            url: URL to measure

        Returns:
            float: Page load time in seconds
        """
        print("Measuring network performance baseline...")

        start_time = time.time()
        self.driver.get(url)

        # Wait for page to be interactive
        WebDriverWait(self.driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        self.baseline_load_time = time.time() - start_time

        # Calculate multiplier based on load time
        if self.baseline_load_time < 2.0:
            self.multiplier = 0.5  # Fast network
            speed = "FAST"
        elif self.baseline_load_time < 5.0:
            self.multiplier = 1.0  # Normal network
            speed = "NORMAL"
        else:
            self.multiplier = 2.0  # Slow network
            speed = "SLOW"

        print(f"Baseline: {self.baseline_load_time:.2f}s ({speed}) - multiplier: {self.multiplier}x")

        return self.baseline_load_time

    def get_adjusted_timeout(self, base_timeout):
        """
        Get timeout adjusted for network performance

        Args:
            base_timeout: Base timeout in seconds

        Returns:
            float: Adjusted timeout
        """
        adjusted = base_timeout * self.multiplier

        # Enforce reasonable bounds
        min_timeout = 1.0
        max_timeout = 20.0
        adjusted = max(min_timeout, min(adjusted, max_timeout))

        return adjusted

    def track_wait_time(self, operation, expected_time, actual_time):
        """Track wait time for analysis"""
        self.wait_times.append({
            'operation': operation,
            'expected': expected_time,
            'actual': actual_time,
            'efficiency': (expected_time - actual_time) / expected_time if expected_time > 0 else 0
        })

    def get_performance_summary(self):
        """Generate performance summary"""
        if not self.wait_times:
            return {}

        total_expected = sum(w['expected'] for w in self.wait_times)
        total_actual = sum(w['actual'] for w in self.wait_times)
        time_saved = total_expected - total_actual
        efficiency = (time_saved / total_expected * 100) if total_expected > 0 else 0

        return {
            'baseline_load_time': self.baseline_load_time,
            'multiplier': self.multiplier,
            'total_operations': len(self.wait_times),
            'expected_wait_time': total_expected,
            'actual_wait_time': total_actual,
            'time_saved': time_saved,
            'efficiency_percent': efficiency,
            'operations': self.wait_times
        }
```

### Adaptive WebDriverWait

```python
def adaptive_wait(driver, condition, base_timeout=5, operation_name="operation"):
    """
    WebDriverWait with adaptive timeout

    Args:
        driver: Selenium WebDriver
        condition: Expected condition to wait for
        base_timeout: Base timeout before adjustment
        operation_name: Name for logging

    Returns:
        Result of condition
    """
    # Get adjusted timeout from global config
    adjusted_timeout = wait_config.get_adjusted_timeout(base_timeout)

    print(f"Waiting for {operation_name} (timeout: {adjusted_timeout:.1f}s)...")

    start_time = time.time()
    try:
        result = WebDriverWait(driver, adjusted_timeout).until(condition)
        actual_time = time.time() - start_time

        wait_config.track_wait_time(operation_name, adjusted_timeout, actual_time)
        print(f"✓ {operation_name} completed in {actual_time:.2f}s")

        return result

    except TimeoutException:
        actual_time = time.time() - start_time
        wait_config.track_wait_time(operation_name, adjusted_timeout, actual_time)
        print(f"✗ {operation_name} timed out after {actual_time:.2f}s")
        raise
```

---

## Implementation Checklist

### Phase 1: Performance Measurement
- [ ] Implement `measure_page_load_performance()`
- [ ] Add Navigation Timing API extraction
- [ ] Test on various network speeds

### Phase 2: Dynamic Configuration
- [ ] Create `DynamicWaitConfig` class
- [ ] Implement `measure_baseline()`
- [ ] Implement `get_adjusted_timeout()`
- [ ] Add wait time tracking

### Phase 3: Integration
- [ ] Create global `wait_config` instance
- [ ] Measure baseline on first page load
- [ ] Replace `WebDriverWait` with `adaptive_wait`
- [ ] Apply to all wait operations

### Phase 4: Metrics and Reporting
- [ ] Implement `track_wait_time()`
- [ ] Implement `get_performance_summary()`
- [ ] Save metrics to JSON
- [ ] Add to scraper output

### Phase 5: Testing
- [ ] Test on fast network (< 2s load)
- [ ] Test on normal network (2-5s load)
- [ ] Test on slow network (> 5s load)
- [ ] Verify appropriate multipliers applied

---

## Testing Requirements

### Unit Tests

```python
def test_multiplier_calculation():
    """Test multiplier based on load time"""
    # Fast network
    assert calculate_multiplier(1.5) == 0.5
    # Normal network
    assert calculate_multiplier(3.0) == 1.0
    # Slow network
    assert calculate_multiplier(7.0) == 2.0

def test_adjusted_timeout():
    """Test timeout adjustment"""
    config = DynamicWaitConfig(mock_driver)
    config.multiplier = 0.5
    assert config.get_adjusted_timeout(10) == 5.0

def test_wait_tracking():
    """Test wait time tracking"""
    config = DynamicWaitConfig(mock_driver)
    config.track_wait_time("test_op", 5.0, 2.5)
    summary = config.get_performance_summary()
    assert summary['time_saved'] == 2.5
```

### Integration Tests

```python
def test_adaptive_waits_on_fast_network():
    """Test with fast network"""
    # Simulate fast page load (< 2s)
    # Verify multiplier = 0.5
    # Verify waits are shorter

def test_adaptive_waits_on_slow_network():
    """Test with slow network"""
    # Throttle network
    # Verify multiplier = 2.0
    # Verify waits are longer
    # Verify no timeout failures
```

### Performance Tests

```python
def test_time_savings_fast_network():
    """Benchmark on fast network"""
    # Run on fast connection
    # Verify 2-5s savings vs fixed timeouts

def test_reliability_slow_network():
    """Test reliability on slow network"""
    # Run on slow connection
    # Verify success rate maintained
    # Verify longer waits prevent timeouts
```

---

## Dependencies

**Requires:**
- Story 1.1 (Explicit Wait Conditions) - provides wait infrastructure

**Blocks:**
- None (enhancement to existing waits)

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Performance API not available | Low | Low | Fallback to 1.0x multiplier; use default timeouts |
| Initial page load not representative | Medium | Medium | Re-measure baseline periodically |
| Multiplier too aggressive | Medium | Low | Enforce min/max bounds (1s-20s) |

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Performance measurement implemented
- [ ] Dynamic wait config working
- [ ] Multipliers applied to all waits
- [ ] Metrics tracked and reported
- [ ] Unit tests passing
- [ ] Integration tests on fast/normal/slow networks
- [ ] Performance improvement measured
- [ ] Code review completed
- [ ] Documentation updated

---

## Estimated Time Savings

**Current:** Fixed timeouts waste time on fast networks
**Optimized:** Adaptive timeouts match network speed
**Savings:** 2-5 seconds per scrape (network dependent)

---

## Related Files

- `index.py` - All wait operations
- Story 1.1 implementation - WebDriverWait calls

---

**Story Status:** ✅ Ready for Implementation
**Next Action:** Requires Story 1.1 completion first
**Priority:** Can be done concurrently with Story 1.2
