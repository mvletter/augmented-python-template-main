# /wrap

End-of-session analysis. Catches items that weren't logged during the session.

## When to use

- End of work session
- Before running `/clear`
- When context is getting full (>50%)
- Automatically called by `/complete`

## Instructions

Read: `.workflow/inbox.md` for existing bugs and ideas

This command is for **losse sessies** (quick fixes, debug work, experiments) without a SPEC.

For SPEC-based work, use `/finish` instead.
## Protocol

### Phase 1: Auto-detect resolved inbox items

**CRITICAL:** Read .workflow/inbox.md first, then scan conversation to find matches.

For each open bug in inbox.md:
1. Check if this session touched related code/functionality
2. Check if error messages from this bug no longer appear
3. Check if user confirmed something "works now" / "fixed" / "solved"

**Match criteria:**
- Same error message mentioned and resolved
- Same functionality discussed and now working
- User explicitly said it's fixed
- Code was changed that directly addresses the bug

**If match found:** Mark as resolved (will be processed in Phase 5)

### Phase 2: Find unlogged items

Scan the ENTIRE conversation for:

**Bugs mentioned but not logged:**
- Error messages discussed
- "This doesn't work" / "broken" / "failing"
- Workarounds applied
- Edge cases discovered

**Ideas mentioned but not logged:**
- "We could..." / "Maybe we should..." / "What if..."
- Future improvements discussed
- Nice-to-haves mentioned
- Alternative approaches considered but not taken

**For each idea, assess detail level:**
- **Simple idea** (just mentioned, no details) → one-liner for inbox
- **Discussed idea** (technical approach, files, API design discussed) → create mini feature spec

### Phase 3: Lessons learned

Scan the conversation for **process issues** - things that went wrong in HOW we worked, not just WHAT we built.

**Look for:**
- User had to correct AI multiple times on same issue
- User expressed frustration ("Had ik daarom gevraagd?", "Luister!", etc.)
- Wrong assumptions that led to wasted work
- AI did something without being asked
- AI misunderstood the request
- Debugging took unusually long due to wrong approach

**For each issue found:**
1. What went wrong? (concrete example)
2. Why did it happen? (root cause)
3. Is this a pattern that could recur?
4. Should this become a pitfall in ../.shared/pitfalls/process-pitfalls.md?

**Pitfall candidates:**
- Issue happened 2+ times in session → definitely add
- User had to correct explicitly → likely add
- Could affect other projects → definitely add

### Phase 4: Present findings

Show the user:

```
## Session wrap-up

### Found in this session:

🐛 Bugs (not yet in inbox):
- [description] - [suggested severity]

💡 Ideas (not yet in inbox):
- [description] - [suggested priority] - **simple** (inbox only)
- [description] - [suggested priority] - **discussed** (will create spec)

✅ Resolved:
- [bug/item that was fixed but not marked]

📚 Lessons learned:
- [what went wrong] → [proposed pitfall or "noted"]

### Already tracked:
- [X bugs in inbox]
- [Y ideas in inbox]
```

**For "discussed" ideas, show what will be captured:**
```
📝 [idea name] spec will include:
- Problem: [what we discussed]
- Approach: [technical details mentioned]
- Files: [files/components mentioned]
- Open questions: [if any]
```

**For pitfall candidates, show:**
```
⚠️ Pitfall candidate: #[category]-[name]
- What happened: [concrete example from session]
- Prevention: [how to avoid next time]
- Add to pitfalls.md? [yes/no]
```

### Phase 5: Confirm and log

Ask: "Add these to inbox? (y/n or edit)"

If yes:
1. Add bugs to .workflow/inbox.md with next available #
2. For **simple ideas**: Add one-liner to .workflow/inbox.md
3. For **discussed ideas**:
   - Create `.workflow/specs/[idea-name].md` using template with Status: Idea
   - Fill in: Problem, Approach (what was discussed), Files mentioned
   - Leave other sections empty (to be filled by /research later)
   - Add to inbox.md with link: `[idea] → [spec](features/[name].md)`
4. Mark resolved items as processed
5. **For confirmed pitfalls**:
   - **Before adding:** Quick grep check: `grep -n "similar-keyword" docs/pitfalls/[category].md`
   - If similar exists, update existing entry instead
   - If new, add to ../.shared/pitfalls/process-pitfalls.md using standard format

## Output

Show confirmation:

```
✅ Session wrapped

Added to inbox:
- 🐛 2 bugs (#4, #5)
- 💡 1 idea (#3) - simple
- 💡 1 idea (#4) → created spec: .workflow/specs/[name].md

Marked as processed:
- Bug #2 (fixed)

Pitfalls added:
- #process-verify-data-first
- #process-listen-to-request

Progress updated. Ready for /clear or continue.
```

### Phase 8: Git commit & push

Commit any uncommitted changes and push to remote:

1. Check for uncommitted changes: `git status --short`
2. If uncommitted changes exist:
   - Stage all changes: `git add -A`
   - Commit with message: `chore: Session wrap - [brief description]`
   - Include Co-Authored-By trailer
3. Push to remote: `git push`
4. Report result: "Committed and pushed X files to origin/[branch]"

**If no remote configured:**
- Skip push, report: "No remote configured, changes committed locally"

**If push fails:**
- Check if upstream is set: `git push -u origin [branch]`
- Report error and let user decide

## Do NOT

- Skip conversation analysis
- Add items without user confirmation
- Forget to update inbox.md
- Skip the lessons learned analysis (this prevents recurring issues)
- Forget to push changes at end of session
