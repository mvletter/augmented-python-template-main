---
name: plan
description: Create SPEC document for feature implementation
---

# /plan - Create SPEC Document

Creates a comprehensive SPEC document using EARS format before implementation.

## Usage

```
/plan "feature description"
```

## What It Does

Delegates to the manager-spec agent which will:
1. Analyze the feature requirements
2. Map domain boundaries and dependencies
3. Create SPEC document at `.workflow/specs/SPEC-XXX/spec.md`
4. Define acceptance criteria
5. Outline technical approach

## Example

```
/plan "Add JWT authentication with refresh tokens"
```

## Next Steps

After reviewing and approving the SPEC:
```
/clear
/implement SPEC-XXX
```

See `../.shared/workflow/README.md` for complete workflow guide.
