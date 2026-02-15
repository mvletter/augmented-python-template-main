# Run Phase - DDD Implementation

Implement SPEC requirements using Domain-Driven Development (DDD) methodology.

## Purpose

The run phase implements the SPEC document through:
- ANALYZE: Understand existing code structure
- PRESERVE: Create characterization tests
- IMPROVE: Apply structural changes with behavior preservation

## Workflow

1. **Initiate Implementation**
   ```
   /run SPEC-XXX
   ```

2. **Manager-DDD Agent Executes**

   **ANALYZE Phase:**
   - Read SPEC requirements
   - Identify affected files
   - Map domain boundaries
   - Calculate coupling metrics

   **PRESERVE Phase:**
   - Verify existing tests pass
   - Create characterization tests for uncovered paths
   - Generate behavior snapshots
   - Confirm safety net adequacy

   **IMPROVE Phase:**
   - Apply transformations incrementally
   - Run tests after each change
   - Commit successful changes
   - Document progress

3. **Validation**
   - All tests passing
   - 85%+ code coverage
   - TRUST 5 quality gates passed
   - No behavior regressions

## Development Methodology

Configured in `.moai/config/sections/quality.yaml`:

```yaml
constitution:
  development_mode: hybrid    # or ddd, tdd
```

**Hybrid Mode** (recommended):
- New code → TDD (RED-GREEN-REFACTOR)
- Existing code → DDD (ANALYZE-PRESERVE-IMPROVE)

## Token Budget

- Allocation: 180,000 tokens
- Strategy: Selective file loading, progressive disclosure
- Optimization: Use Serena MCP for large files (90% token savings)

## Success Criteria

- All SPEC requirements implemented
- All tests passing
- 85%+ code coverage
- No regressions
- TRUST 5 validated

## Next Step

After implementation complete:
```
/sync SPEC-XXX
```

---

See parent README.md for complete SPEC workflow guide.
