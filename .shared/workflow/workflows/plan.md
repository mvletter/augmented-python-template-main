# Plan Phase - SPEC Creation

Create comprehensive specification documents using EARS format before implementation.

## Purpose

The plan phase creates a structured SPEC document that defines:
- Requirements in EARS format (Event-driven, State-driven, Unwanted, Optional)
- Acceptance criteria
- Technical approach
- Success metrics

## Workflow

1. **Initiate Planning**
   ```
   /plan "feature description"
   ```

2. **Manager-Spec Agent Creates SPEC**
   - Analyzes requirements
   - Maps domain boundaries
   - Defines acceptance criteria
   - Creates `.workflow/specs/SPEC-XXX/spec.md`

3. **Review and Approval**
   - User reviews generated SPEC
   - Requests modifications if needed
   - Approves for implementation

4. **Context Reset**
   ```
   /clear
   ```
   Execute before moving to run phase (saves 45-50K tokens)

## Token Budget

- Allocation: 30,000 tokens
- Strategy: Load requirements only, avoid full codebase exploration
- Savings: Enables 70% larger implementations

## Output

SPEC document at `.workflow/specs/SPEC-XXX/spec.md` containing:
- Executive summary
- EARS format requirements
- Acceptance criteria
- Technical approach
- File changes list
- Success criteria

## Next Step

After SPEC approval:
```
/clear
/run SPEC-XXX
```

---

See parent README.md for complete SPEC workflow guide.
