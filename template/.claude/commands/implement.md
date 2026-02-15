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
/finish SPEC-XXX
```

See `../.shared/workflow/README.md` for complete workflow guide.

## Git Commit Strategy

Create separate commits for each DDD phase:

### ANALYZE Commit

After documenting existing behavior:

```bash
git add -A
git commit -m "🔴 ANALYZE: [behavior description] ([spec-name])"
```

Example:
```bash
git commit -m "🔴 ANALYZE: Document user authentication flow (user-login)"
```

### PRESERVE Commit

After creating characterization tests:

```bash
git add -A
git commit -m "🟢 PRESERVE: [test description] ([spec-name])"
```

Example:
```bash
git commit -m "🟢 PRESERVE: Add characterization tests for auth endpoints (user-login)"
```

### IMPROVE Commit

After implementing improvements:

```bash
git add -A
git commit -m "♻ IMPROVE: [improvement description] ([spec-name])"
```

Example:
```bash
git commit -m "♻ IMPROVE: Add JWT token refresh mechanism (user-login)"
```

## Commit Message Format

All commits follow this pattern:
- **Emoji indicator**: 🔴 (ANALYZE), 🟢 (PRESERVE), ♻ (IMPROVE)
- **Phase**: ANALYZE, PRESERVE, or IMPROVE
- **Description**: What was done in this phase
- **SPEC reference**: ([spec-name]) in parentheses

## Why Separate Commits?

- **Clear history**: See exactly what happened in each phase
- **Easy rollback**: Can revert to any phase if needed
- **Documentation**: Commits tell the story of the change
- **Review**: Easier to review changes phase-by-phase
