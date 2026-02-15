# Shared Rules

This directory contains references to shared rules from the parent .shared directory.

To access shared rules, patterns, and pitfalls:
- Rules: `../../.shared/rules/rules.md`
- Pitfalls: `../../.shared/pitfalls.md`  
- Patterns: `../../.shared/patterns.md`

You can create symbolic links manually if needed:
```bash
cd .claude/rules
ln -s ../../.shared/rules/rules.md shared-rules.md
ln -s ../../.shared/pitfalls.md shared-pitfalls.md
ln -s ../../.shared/patterns.md shared-patterns.md
```
