---
name: review-endpoint
description: Reviews a FastAPI route file for error handling and input validation issues.
---

Review the FastAPI route file given as an argument (e.g. `/review-endpoint backend/app/api/v1/sessions.py`).

## Steps

1. Read the specified route file
2. For each route handler, check for:
   - Missing error handling (no HTTPException on operations that can fail)
   - Missing input validation (untyped params, no schema constraints)
   - Missing auth checks
3. Output a simple findings list grouped by route
4. Ask the user if they want fixes applied

## Constraints
- Do not modify any file until the user confirms
- Only report issues you can see in the file