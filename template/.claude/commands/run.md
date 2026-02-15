---
name: run
description: Implement SPEC using DDD methodology
---

# /run - Implement SPEC

Implements a SPEC document using Domain-Driven Development (DDD) methodology.

## Usage

```
/run SPEC-XXX
```

## What It Does

Delegates to the manager-ddd agent which executes:

**ANALYZE Phase:**
- Reads SPEC requirements
- Identifies affected files
- Maps domain boundaries

**PRESERVE Phase:**
- Verifies existing tests pass
- Creates characterization tests
- Generates behavior snapshots

**IMPROVE Phase:**
- Applies incremental transformations
- Runs tests after each change
- Validates behavior preservation

## Example

```
/run SPEC-001
```

## Success Criteria

- All SPEC requirements implemented
- All tests passing (85%+ coverage)
- No behavior regressions
- TRUST 5 quality gates passed

## Next Steps

After implementation complete:
```
/sync SPEC-XXX
```

See `../.shared/moai/README.md` for complete workflow guide.
