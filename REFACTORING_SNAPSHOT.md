# Refactoring Snapshot - Remove MoAI Branding

Date: 2026-02-15
Purpose: Transform augmented-python-template from MoAI-branded to generic workflow

## Current Structure

### Command Files (template/.claude/commands/)
- plan.md - References `/moai:1-plan`, `.moai/specs/`
- run.md - References `/moai:2-run`, `manager-ddd`, `../.shared/moai/README.md`
- sync.md - References `/moai:3-sync`, `manager-docs`, `../.shared/moai/README.md`

### Directory Structure
- template/.moai/ → Contains config/sections/
- .shared/moai/ → Contains workflows/ and README.md

### Agent Files (template/.claude/agents/moai/)
- manager-spec.md - Skills: moai-foundation-*, moai-workflow-*, moai-lang-*
- manager-ddd.md - Skills: moai-foundation-*, moai-workflow-*, moai-tool-*
- manager-docs.md - References to MoAI-ADK ecosystem

### Configuration Files
- template/.moai/config/sections/language.yaml
- template/.moai/config/sections/quality.yaml

### Documentation
- template/CLAUDE.md.jinja - Section "SPEC Workflow" references moai commands
- .shared/moai/README.md - MoAI workflow documentation
- .shared/moai/workflows/*.md - Plan, Run, Sync workflow docs

### Copier Configuration
- copier.yml - Line 76: "Include Claude Code workflow (MoAI SPEC workflow)?"

## Expected Changes

### Renamings
1. run.md → implement.md
2. template/.moai/ → template/.workflow/
3. .shared/moai/ → .shared/workflow/

### Content Updates
1. Commands: /moai plan → /plan, /moai run → /implement, /moai sync → /sync
2. Remove "🗿 MoAI <email@mo.ai.kr>" signatures
3. Change "MoAI" → "Workflow" or remove
4. Update path references: .moai → .workflow
5. Update skill references: moai-* → workflow-* where appropriate

### Additions
1. template/.claude/commands/refactor.md (from Herald)
