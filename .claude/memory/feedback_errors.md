---
name: Feedback — Error Handling
description: Always log exceptions before re-raising; never silently swallow errors into generic 503s
type: feedback
---

Never wrap a broad `except Exception` without logging the actual exception first.

**Why:** The auth router was catching all exceptions and returning a generic 503 with no log output, making it impossible to diagnose the real error (which was a DB connection failure). This cost multiple debug cycles.

**How to apply:** Any `except Exception` block that re-raises as an HTTPException must log the exception first:
```python
except Exception as exc:
    logging.getLogger(__name__).exception("Descriptive message: %s", exc)
    raise HTTPException(...)
```
