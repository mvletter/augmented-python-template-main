---
name: refactor
description: Analyze code quality and generate refactoring spec
---

# /refactor - Code Quality Analysis

Analyze code quality and generate a feature spec for improvements.

## When to use

| Situation | Command |
|-----------|---------|
| Standalone session (bugs, maintenance) | `/refactor` standalone |
| Periodic quality improvement | `/refactor` standalone |
| Technical debt reduction | `/refactor` standalone |

## Protocol

### Phase 1: ANALYZE - Code smell detection

**Function issues:**
- Functions > 20 lines
- Functions with multiple responsibilities
- Deep nesting (> 3 levels)
- Too many parameters (> 4)

**Duplication:**
- Similar code in multiple places
- Copy-pasted logic with minor variations
- Patterns that should be extracted

**Coupling:**
- Business logic mixed with infrastructure
- Hard-coded dependencies
- Tight coupling between unrelated modules

**Consistency:**
- Different error handling approaches
- Inconsistent logging patterns
- Mixed architectural styles

### Prioritize

**High impact, low risk**: Do first
**High impact, high risk**: Break into smaller steps
**Low impact, any risk**: Consider skipping

### Phase 2: PRESERVE - Lock current behavior

Before changing any code, capture what it currently does.

**For each refactor target:**

1. **Check existing tests**
   ```
   # Find tests that cover this code
   grep -r "test.*ClassName" tests/
   grep -r "ClassName" tests/
   ```

2. **If no tests exist → write characterization tests**

   Characterization tests capture CURRENT behavior, not intended behavior:
   ```python
   def test_current_behavior_of_process_data():
       """Characterization test - captures current behavior before refactor."""
       result = process_data(sample_input)
       # Assert what it ACTUALLY returns, even if weird
       assert result == {"status": "ok", "count": 42}
   ```

3. **Run tests to establish baseline**
   ```bash
   pytest tests/test_[module].py -v
   ```
   All tests must pass BEFORE refactoring.

**Output of PRESERVE phase:**
- [ ] Each refactor target has test coverage
- [ ] All tests pass (baseline established)
- [ ] Commit: `test: add characterization tests for [component]`

### Phase 3: IMPROVE - Refactor with safety net

Now refactor, running tests after each change:

```
1. Make ONE small change
2. Run tests
3. Tests pass? → Commit, continue
4. Tests fail? → Revert, try different approach
```

**Never refactor multiple things between test runs.**

## Output

Create `.workflow/specs/SPEC-REFACTOR-[YYYY-MM-DD]/spec.md` using EARS format.

Include:
- Top 3 issues with specific examples
- Tasks for each refactor
- Expected outcomes and quality metrics

## Do NOT

- Change behavior (refactor preserves behavior)
- Add features
- Fix bugs (unless the bug IS the code smell)
- Refactor without existing test coverage
