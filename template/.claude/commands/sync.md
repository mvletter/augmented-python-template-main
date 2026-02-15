---
name: sync
description: Generate documentation after SPEC implementation
---

# /sync - Generate Documentation

Generates documentation and prepares for deployment after SPEC implementation.

## Usage

```
/sync SPEC-XXX
```

## What It Does

Delegates to the manager-docs agent which will:
1. Scan implemented code
2. Generate API documentation
3. Update README with new features
4. Create CHANGELOG entry
5. Optionally create pull request

## Example

```
/sync SPEC-001
```

## Output

- `docs/api.md` - API reference
- `README.md` - Updated features
- `CHANGELOG.md` - New entry
- Pull request (if configured)

## Completion

SPEC workflow cycle is complete. Ready for code review and deployment.

See `../.shared/workflow/README.md` for complete workflow guide.
