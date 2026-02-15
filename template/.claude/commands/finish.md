# /complete [feature-name]

Finish a feature: cleanup, refactor, wrap, and document.

> **Note:** `$ARGUMENTS` = the name you provide when running this command.
> Example: `/complete user-auth` → `$ARGUMENTS` becomes `user-auth`

## Prerequisites

Feature must have all tasks completed in docs/features/[name].md.

## Instructions

Read these docs:
- docs/features/$ARGUMENTS.md (the completed feature - required)
- docs/pitfalls.md (check for issues)
- docs/patterns.md (verify patterns used correctly)
- claude-progress.txt (session history)

## Protocol

### Phase 1: Verify completion

Check that:
- [ ] All tasks marked complete in feature spec
- [ ] All tests passing
- [ ] Code merged to main
- [ ] No blockers remaining

If not complete, stop and report what's missing.

---

### Phase 2: Cleanup

Run the `/cleanup` protocol on the feature code.

See `commands/cleanup.md` for the full checklist (unused code, dead code, debug statements, etc.)

**Action:** Fix all issues found. Commit: `cleanup: [feature-name]`

---

### Phase 3: Refactor

Run the `/refactor` protocol on the feature code.

See `commands/refactor.md` for the full checklist (long functions, duplication, deep nesting, etc.)

**Action:** Fix high-impact issues. Commit: `refactor: [feature-name]`

**Run tests again** after refactoring to ensure behavior unchanged.

---

### Phase 4: Performance check

Invoke the performance-optimizer as a subagent:

```
Use a subagent with the instructions from .claude/agents/performance-optimizer.md to check the feature code.
```

The subagent scans for bottlenecks (N+1 queries, missing indexes, memory leaks, etc.)

**If critical issues found:** Fix before proceeding.
**If medium/low issues:** Note in feature spec under "Technical debt", proceed.
**If no issues:** Proceed.

---

### Phase 5: Code review

Invoke the code-reviewer as a subagent:

```
Use a subagent with the instructions from .claude/agents/code-reviewer.md to review my changes.
```

The subagent reads pitfalls.md and patterns.md, checks all changed files, and returns a verdict.

**If verdict is NEEDS FIXES:** Address issues before proceeding.
**If verdict is PASS WITH WARNINGS:** Note warnings, proceed.
**If verdict is PASS:** Proceed.

---

### Phase 6: Wrap

Run the `/wrap` logic to catch anything missed during implementation:

1. Read docs/inbox.md (current state)
2. Scan conversation for unlogged bugs/ideas
3. Auto-detect resolved inbox items (bugs fixed during this feature)
4. Present findings to user
5. Add confirmed items to docs/inbox.md
6. Mark resolved items as processed

---

### Phase 6.5: Check for Existing Patterns

Before adding to docs, search for similar content:

```bash
# Quick grep for similar topics
grep -rn "keyword-from-your-change" docs/pitfalls/
grep -rn "keyword-from-your-change" docs/patterns/
```

If similar content exists:
- Update existing entry instead of creating new one
- Add cross-reference if different angle needed

---

### Phase 7: Auto-generate "What We Built"

**CRITICAL:** Analyze the ENTIRE conversation history to extract:

#### How we solved it (2-3 sentences)

Write in plain language that a non-coder can understand:
- What approach did we take?
- How does it work from a user perspective?
- What problem does it solve?

**Avoid:** Technical jargon, implementation details, framework names
**Focus on:** User experience, what happens, why it matters

**Example:**
> "Users now register with email and password. The password gets encrypted and stored safely. When they log in, we give them a special token that proves who they are for the next 24 hours."

#### Key decisions (2-4 items)

Extract important decisions from the conversation:
- What did we choose?
- Why did we choose it? (concrete reasoning)
- What alternatives did we reject and why?

**Example:**
> "- JWT tokens instead of sessions - allows mobile app to authenticate without cookies
> - bcrypt cost factor 10 - tested that cost 12 takes 200ms which is too slow"

#### Bugs we fixed along the way

List bugs discovered during implementation:
- What went wrong?
- How did we discover it?
- How did we fix it?

If no bugs: Write "none"

**Check for /retro:** For each bug listed, check if it needs `/retro`:
- Took >30 min? → `/retro`
- Same bug seen before? → `/retro`
- Data loss or corruption? → `/retro`
- Security issue? → `/retro`

#### What we learned (2-3 items)

Capture learnings from the process:
- Technical insights discovered
- Process improvements identified
- Things to do differently next time

---

### Phase 8: Calculate metadata

**Built date range:**
- Look at first commit in feature branch (start date)
- Look at last commit in feature branch (end date)
- Calculate total time from session notes or conversation

**Format:** "Dec 20-22, 2024 (6 hours)"

---

### Phase 9: Update feature spec

Add the complete "What We Built" section to docs/features/$ARGUMENTS.md:

```markdown
---
## Filled by /complete (Auto-generated)
---

## What We Built

**Built**: [dates and hours]

**How we solved it**:

[2-3 sentence explanation]

**Key decisions**:

- [Decision 1]
- [Decision 2]
- [Decision 3]

**Bugs we fixed along the way**:

- [Bug 1]
- [Bug 2]

**What we learned**:

- [Learning 1]
- [Learning 2]
```

---

### Phase 10: Documentation sync check

Invoke the doc-sync-checker as a subagent:

```
Use a subagent with the instructions from .claude/agents/doc-sync-checker.md to verify docs are up to date.
```

The subagent compares architecture.md and database.md against actual code structure.

**If verdict is NEEDS UPDATE:** Fix the out-of-sync docs before proceeding.

---

### Phase 11: Agent learning check

Quick check: did this feature produce learnings that agents should know?

- New patterns added? → code-reviewer will pick them up automatically
- New architecture components? → doc-sync-checker will pick them up automatically
- Repeated issues during implementation? → Consider if an agent could have caught this earlier

If you notice a gap (something an agent SHOULD have caught but didn't):
- Note it in the feature spec under "What we learned"
- Consider running `/evolve` after a few features to evaluate agent improvements

---

### Phase 12: Final documentation updates

Complete the "After completion" checklist:

1. **Capture technical learnings:**
   - Add new patterns to docs/patterns.md (with category-prefixed anchors)
   - Add new pitfalls to docs/pitfalls.md (with category-prefixed anchors)
   - Update docs/architecture.md if structure changed
   - Update docs/database.md if schema changed

2. **Add AI-CONTEXT comments:**
   In the code, add comments pointing to new docs entries:
   ```
   // AI-CONTEXT: See docs/pitfalls.md#[category]-[name]
   // AI-CONTEXT: See docs/patterns/[category].md#[pattern-name]
   ```

3. **Move feature spec:**
   - Update Status in feature spec to: Done
   - Move docs/features/$ARGUMENTS.md to docs/features/done/
   - Keep filename the same

4. **Commit all changes:**
   - Stage all modified files related to the feature
   - Commit with message: `feat([scope]): [description] ([spec-name])`
   - Include SPEC reference in parentheses at end
   
   Example:
   ```bash
   git add -A
   git commit -m "feat(auth): Add JWT authentication with refresh tokens (user-login)
   
   - Implemented token generation and validation
   - Added refresh token endpoint
   - All tests passing (87% coverage)
   
   ```
   
   Format breakdown:
   - `feat([scope])`: Conventional commit type and scope
   - `[description]`: Clear summary of what was built
   - `([spec-name])`: Reference to the SPEC (e.g., user-login, payment-flow)

5. **Update tracking:**
   - Update project.md: move from Active to Done
   - Update claude-progress.txt:
     - Set Type to "none", Source to empty
     - Clear "Quick resume"
     - Add final entry to session history

---

## Output

Show the user:

```
## /complete summary

### Code quality
- Cleanup: [X issues fixed]
- Refactor: [X improvements made]
- Performance: [X issues found, Y fixed]
- Tests: passing

### Inbox
- Found: [X bugs, Y ideas]
- Resolved: [X items marked done]

### Documentation
- "What We Built" section added
- Patterns added: [list or "none"]
- Pitfalls added: [list or "none"]
- Spec moved to: docs/features/done/[name].md

### Done
Feature [name] completed.
```

---

## Do NOT

- Skip cleanup or refactor phases
- Generate generic summaries ("we added a feature to handle authentication")
- Use technical jargon without explanation in "How we solved it"
- Skip the conversation analysis - actually read through what happened
- Miss important decisions or bugs that were discussed
- Refactor without running tests afterward
- Over-engineer during refactor (keep changes minimal)
