# SPEC Workflow Guide

Structured development workflow for feature implementation using specification-driven approach.

## Overview

The SPEC workflow is a three-phase development methodology:

1. **Plan** - Create detailed specification
2. **Run** - Implement with DDD methodology
3. **Sync** - Generate documentation and deploy

## Quick Start

### Create a SPEC

```bash
/plan "Add user authentication with JWT tokens"
```

The manager-spec agent will:
- Analyze requirements
- Create SPEC document at `.workflow/specs/SPEC-001/spec.md`
- Define acceptance criteria
- Map technical approach

### Implement the SPEC

After reviewing and approving the SPEC:

```bash
/clear
/run SPEC-001
```

The manager-ddd agent will:
- **ANALYZE** existing code structure
- **PRESERVE** behavior with characterization tests
- **IMPROVE** code incrementally with continuous validation

### Generate Documentation

After implementation is complete:

```bash
/sync SPEC-001
```

The manager-docs agent will:
- Generate API documentation
- Update README
- Create CHANGELOG entry
- Optionally create pull request

## When to Use SPEC Workflow

**Recommended for:**
- Multi-developer features
- Features requiring handoff between team members
- Major architectural changes
- Features requiring more than 2 days of work
- Complex domain logic requiring careful planning

**Not recommended for:**
- Quick bug fixes (1-2 files)
- Single-file changes
- Exploratory coding and prototyping
- Trivial updates

## Development Methodology

The SPEC workflow uses **Hybrid mode** by default:

- **New code** → TDD (Test-Driven Development)
  - RED: Write failing test
  - GREEN: Make test pass
  - REFACTOR: Improve code quality

- **Existing code** → DDD (Domain-Driven Development)
  - ANALYZE: Understand structure
  - PRESERVE: Create safety net
  - IMPROVE: Transform incrementally

Configuration in `.workflow/config/sections/quality.yaml`:
```yaml
constitution:
  development_mode: hybrid
  hybrid_settings:
    new_features: tdd
    legacy_refactoring: ddd
```

## Token Budget Management

The 200K token context window is allocated across phases:

| Phase | Budget | Purpose |
|-------|--------|---------|
| Plan | 30K | SPEC creation |
| Run | 180K | Implementation |
| Sync | 40K | Documentation |

**Best Practice:** Execute `/clear` after plan phase to reset context and save tokens for implementation.

## Quality Standards

All SPEC implementations must pass:

- **85%+ code coverage** - Comprehensive test coverage
- **TRUST 5 validation** - Quality framework compliance
- **No regressions** - All existing tests pass
- **Behavior preservation** - Characterization tests validate

## Workflow Details

See individual phase documentation:

- [Plan Phase](workflows/plan.md) - SPEC document creation
- [Run Phase](workflows/run.md) - DDD implementation cycle
- [Sync Phase](workflows/sync.md) - Documentation generation

## Example Workflow

```bash
# 1. Create SPEC for new feature
/plan "Add email notification system with templates"

# Review generated SPEC at .workflow/specs/SPEC-002/spec.md
# Make any requested changes
# Approve SPEC

# 2. Clear context and implement
/clear
/run SPEC-002

# Manager-DDD executes ANALYZE-PRESERVE-IMPROVE cycle
# All tests pass, coverage >85%

# 3. Generate documentation
/sync SPEC-002

# Documentation updated, ready for PR
```

## Agents

This workflow uses three specialized agents:

### manager-spec
- Creates SPEC documents in EARS format
- Maps requirements to acceptance criteria
- Defines technical approach
- Located: `.claude/agents/moai/manager-spec.md`

### manager-ddd
- Executes DDD cycle (ANALYZE-PRESERVE-IMPROVE)
- Creates characterization tests
- Applies incremental transformations
- Validates behavior preservation
- Located: `.claude/agents/moai/manager-ddd.md`

### manager-docs
- Generates API documentation
- Updates README and CHANGELOG
- Creates pull requests
- Located: `.claude/agents/moai/manager-docs.md`

## Configuration

### Quality Settings

`.workflow/config/sections/quality.yaml`:
- Development mode (hybrid, ddd, tdd)
- Coverage thresholds
- TRUST 5 enforcement
- Testing requirements

### Language Settings

`.workflow/config/sections/language.yaml`:
- Conversation language (en, nl, ko, etc.)
- Code comment language
- Documentation language

### User Settings

`.workflow/config/sections/user.yaml`:
- User name for commits
- Preferences

## Resources

- **EARS Format**: Event-driven, state-driven requirements
- **DDD Methodology**: Domain-Driven Development cycle
- **TRUST 5**: Quality framework (Tested, Readable, Unified, Secured, Trackable)
- **Token Optimization**: Context budget management strategies

---

**Version:** 1.0
**Last Updated:** 2026-02-15
**Scope:** Minimal SPEC Workflow (3 agents only)
