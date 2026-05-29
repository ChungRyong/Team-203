---
name: workspace-parity
description: Ensure absolute parity, synchronization, and strict policy compliance across Team-203's dual active workspaces. Make sure to use this skill whenever working in the Team-203 project, when editing any workspace files, when committing, when testing, or when synchronizing files between the primary vault workspace and the secondary workspace.
---

# Workspace Parity Skill

This skill guarantees that all modifications made in the primary vault workspace are perfectly synchronized with the secondary active workspace, while strictly enforcing critical virtual office policies.

## Workspace Layout
- **Primary Vault Workspace:** `/Users/jabiseu/Documents/obsidian-wiki-vault/projects/Team-203`
- **Secondary Active Workspace:** `/Users/jabiseu/Documents/workspace/Team-203`

## Quick Parity Synchronization
To automatically copy all modified and untracked files from the primary workspace to the secondary workspace, and perform a strict compliance audit, run the bundled parity script:
```bash
python3 .skills/workspace-parity/scripts/sync.py
```

## Strict Policies & Rules
Whenever editing code or assets, you MUST adhere to the following rules without exception:

### 1. ⚠️ The Git Push Lock (Always Ask)
- **Rule:** Under NO circumstances should `git push` be called automatically or autonomously.
- **Action:** Stage and commit changes locally. Always ask the user for explicit "push" confirmation in the chat before executing any push.

### 2. ⚠️ Warning 1: No Pytest During Static Asset Edits
- **Rule:** If any frontend static assets (e.g. `.html`, `.css`, `.js`, `.jpeg`, `.png`, `.jpg`, `.md`) are modified, do NOT run `pytest` or backend unit tests.
- **Reason:** The backend tests trigger active auto-commit/git-backup middleware hooks, causing unwanted git backups and performance clutter.

### 3. ⚠️ Active Parity Enforcement
- **Rule:** Every modified file in the primary workspace must have an identical synchronized copy in the secondary workspace at all times to maintain workspace consistency.

## Verification Checklist
- [ ] Run the `sync.py` script to audit parity.
- [ ] Verify both file paths have identical contents and sizes.
- [ ] Commit locally but DO NOT push to origin/main without explicit user consent.
