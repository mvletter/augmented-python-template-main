---
name: implement
description: Implement SPEC using DDD methodology
---

# /implement - Implement SPEC

Implements a SPEC document using Domain-Driven Development (DDD) methodology.

## Usage

```
/implement SPEC-XXX
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
/implement SPEC-001
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

See `../.shared/workflow/README.md` for complete workflow guide.
