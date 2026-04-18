---
name: Auth Setup — bcrypt without passlib
description: Password hashing uses bcrypt directly; passlib was removed due to version incompatibility
type: project
---

`passlib` was removed from the project because it is incompatible with `bcrypt >= 4.1` (the `__about__` attribute was removed from bcrypt, breaking passlib's backend detection).

**Current setup in `backend/app/services/auth_service.py`:**
```python
import bcrypt

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

**`pyproject.toml` dependency:** `"bcrypt>=4.0.0"` (no passlib)

**Why:** passlib is unmaintained and breaks with modern bcrypt. Using bcrypt directly is simpler and future-proof.
**How to apply:** Never re-add passlib. If password hashing is touched, use the bcrypt API directly.
