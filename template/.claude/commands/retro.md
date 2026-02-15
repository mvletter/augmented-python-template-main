# /retro [short description of what went wrong]

Analyze a bug or problem and prevent it from happening again.

## When to use

| Situation | Action |
|-----------|--------|
| Bug fixed in <15 min | Skip |
| Bug took >30 min | `/retro` |
| Same problem seen twice | `/retro` (required) |
| Data lost or corrupted | `/retro` (required) |
| Security issue | `/retro` (required) |

## Instructions

Read: docs/pitfalls.md (to check if similar pitfall exists)

## Protocol

### Phase 1: Answer three questions

Answer in **plain language** (no code, no technical jargon):

**1. What went wrong?**
> Describe what you saw happen. Not the code, but the effect.
>
> Example: "When I updated a contact, the photo disappeared."

**2. Why could this happen?**
> What wasn't checked or tested?
>
> Example: "There was no check if the photo already existed before saving."

**3. How do we prevent this?**
> One concrete action. Not "be more careful" but something verifiable.
>
> Example: "Always check if a field already has a value before clearing it."

### Phase 2: Determine severity

Pick one:

| Severity | Meaning | Example |
|----------|---------|---------|
| **low** | Annoying but no damage | Button in wrong position |
| **medium** | Feature doesn't work well | Filter shows wrong results |
| **high** | Data lost or corrupted | Photos disappear on update |
| **critical** | Security or completely broken | Passwords visible, app crashes |

### Phase 3: Create pitfall entry

Add to `docs/pitfalls.md` using this format:

```markdown
---

## [category]-[short-name]

**Severity:** [low/medium/high/critical]
**Date:** [today]

**What went wrong:**
[Answer to question 1 - plain language]

**Why this could happen:**
[Answer to question 2]

**Prevention:**
[Answer to question 3]

**Trigger:** [When should AI think about this? E.g., "When updating records with optional fields"]
```

### Phase 4: Add AI-CONTEXT

Add a comment in the fixed code:

```
// AI-CONTEXT: See docs/pitfalls.md#[category]-[short-name]
```

## Example: Complete retro

**User says:** `/retro photos disappear when updating contact`

**AI walks through:**

### Three questions

1. **What went wrong?**
   When I updated a contact (for example, just the phone number), the profile photo disappeared. The photo file was still there, but the system "forgot" where it was stored.

2. **Why could this happen?**
   When saving, every field that wasn't filled in was automatically cleared. There was no check whether the field already had a value that should be preserved.

3. **How do we prevent this?**
   On updates: first check if a field already has a value. Only overwrite if a new value is explicitly provided.

### Severity: high
(Data lost - photo link gone)

### Pitfall entry

```markdown
---

## data-partial-update-loss

**Severity:** high
**Date:** 2025-01-15

**What went wrong:**
When updating a contact, the profile photo disappeared even though it wasn't being changed. The system forgot where the photo was stored.

**Why this could happen:**
Fields that weren't filled in were automatically cleared. No check if the field already had a value.

**Prevention:**
On updates, always check if a field already has a value. Only overwrite if a new value is explicitly provided.

**Trigger:** When updating records, especially with optional fields like photos, attachments, or notes.
```

### AI-CONTEXT

```javascript
// AI-CONTEXT: See docs/pitfalls.md#data-partial-update-loss
const newValue = input.photo !== undefined ? input.photo : existing.photo;
```

### Phase 5: Agent relevance check

Ask: "Is this pitfall relevant for an existing agent?"

Check `.claude/agents/` for agents that should know about this pitfall.

If relevant:
- Note which agent should check for this
- The agent already reads pitfalls.md dynamically, so no update needed
- But if the pitfall needs a SPECIFIC check (not just pattern matching), add it to the agent's checklist

If no agent covers this area AND you see 3+ related pitfalls:
- Suggest: "Consider running /evolve to evaluate if a new agent is needed"

## Output

Show user:
1. The three answers (for verification)
2. The pitfall entry being added
3. Where the AI-CONTEXT comment goes
4. Agent relevance: [which agent, or "none currently"]
5. Confirmation: "Added to pitfalls.md"

## Do NOT

- Use technical jargon in the three answers
- Include code snippets in "What went wrong" or "Why this could happen"
- Use vague prevention like "test better" or "be more careful"
- Skip the AI-CONTEXT comment
- Create duplicate entries (check if similar pitfall exists first)

## Categories for anchors

Use these prefixes:

| Category | When |
|----------|------|
| `data-` | Data loss, corruption, wrong values |
| `async-` | Timing, order, waiting for things |
| `security-` | Passwords, access, authentication |
| `ui-` | Buttons, screens, what user sees |
| `api-` | Communication between systems |
| `state-` | Remembering things, caching, sessions |
| `error-` | Error messages, crashes, handling |
