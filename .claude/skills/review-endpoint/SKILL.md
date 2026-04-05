---
name: review-endpoint
description: Reviews a FastAPI route file for error handling gaps, input validation issues, and missing test coverage. Outputs a structured findings report and offers to apply fixes.
---

Review the backend API route file provided as an argument (e.g. `/review-endpoint backend/app/api/v1/sessions.py`).

## Steps

**1. Identify the target file**

The argument is the path to a FastAPI route file. If no argument is given, ask the user which route file to review before proceeding.

**2. Read the route file**

Read the full contents of the specified route file. Note every route handler: its HTTP method, path, dependencies, request body/query params, and response model.

**3. Discover related files**

For each route handler, locate and read:
- The service function(s) it calls (under `backend/app/services/`)
- The Pydantic request and response schemas it uses (under `backend/app/schemas/`)
- The ORM models involved (under `backend/app/models/`)
- The corresponding test file (under `backend/app/tests/`, named `test_<router_filename>.py`)

Do not modify any of these files.

**4. Analyze for issues across three dimensions**

**A. Error Handling**
Check each route handler for:
- Missing `HTTPException` on operations that can fail (DB not found, permission denied, agent failure)
- Catching broad exceptions (`except Exception`) without re-raising as `HTTPException`
- No retry logic or failure logging on agent calls
- Operations that can raise unhandled exceptions from the service or ORM layer
- Missing 404 when fetching a resource by ID that may not exist
- Missing 403/401 for ownership checks (e.g. candidate accessing another candidate's session)

**B. Input Validation**
Check each route handler and its schemas for:
- Path/query params that are raw strings instead of typed (`UUID`, `int`, `Literal[...]`)
- Pydantic schemas missing field validators (`@field_validator`, `min_length`, `ge`, `le`, `pattern`)
- User-supplied strings passed directly into agent prompts without sanitization
- Missing required fields that would silently default to `None`
- No validation that enum-constrained fields use actual enum types

**C. Test Coverage**
Cross-reference every route handler against the test file:
- Auth guard (401 when unauthenticated) — one test per protected route
- Happy path (200/201 with valid input)
- Not-found path (404 when resource doesn't exist)
- Forbidden path (403 when accessing another user's resource)
- Validation rejection (422 for malformed input)
- Agent/service failure path (500 or appropriate error when downstream fails)

Flag any of the above that are missing.

**5. Output a structured report**

Print the report in this exact format — do not truncate findings:

```
## Endpoint Review: <filename>

### Error Handling
| Route | Issue | Severity | Suggested Fix |
|-------|-------|----------|---------------|
| GET /path | Missing 404 when session not found | HIGH | Raise HTTPException(404) after scalar_one_or_none() returns None |
| ...   | ...   | ...      | ...           |

### Input Validation
| Route / Schema | Issue | Severity | Suggested Fix |
|----------------|-------|----------|---------------|
| SessionCreate.role | Plain `str`, no length constraint | MEDIUM | Use `role: str = Field(..., min_length=1, max_length=100)` |
| ...            | ...   | ...      | ...           |

### Test Coverage Gaps
| Route | Missing Test | Suggested Test Name |
|-------|-------------|---------------------|
| GET /api/v1/sessions/{id} | 403 for wrong candidate | test_get_session_detail_raises_403_for_wrong_candidate |
| ...   | ...         | ...                 |

### Summary
- Error handling issues: <N> (HIGH: X, MEDIUM: Y, LOW: Z)
- Input validation issues: <N>
- Missing tests: <N>
```

Use severity levels: **HIGH** (can cause data leakage, unhandled crash, or auth bypass), **MEDIUM** (degrades reliability or allows bad data in), **LOW** (code quality / best practice).

If a dimension has no issues, write `No issues found.` under that heading.

**6. Offer to apply fixes**

After the report, ask the user exactly:

> Would you like me to apply any of these fixes? Reply with:
> - **"all"** to apply every finding
> - **"errors"**, **"validation"**, or **"tests"** to fix one category
> - A specific route name (e.g. `GET /api/v1/sessions/{id}`) to fix just that route
> - **"no"** to skip

## Constraints

- **Do not modify any file until the user explicitly confirms** in response to the question above.
- **Do not invent issues.** Only report findings supported by what you read in the actual files.
- **Do not rewrite working code** as part of a fix — make the minimum change that resolves the specific issue.
- When applying fixes, touch only the files necessary: the route file, its schema file, and/or its test file.
- When adding tests, follow the TDD commit convention from CLAUDE.md: write the test in the existing test file; do not create new test files unless none exists.
- Preserve all existing imports, formatting, and code style when editing files.