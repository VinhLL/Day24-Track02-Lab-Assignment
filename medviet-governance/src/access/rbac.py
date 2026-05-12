from functools import wraps
from pathlib import Path
from typing import Optional

from fastapi import Header, HTTPException


MOCK_USERS = {
    "token-alice": {"username": "alice", "role": "admin"},
    "token-bob": {"username": "bob", "role": "ml_engineer"},
    "token-carol": {"username": "carol", "role": "data_analyst"},
    "token-dave": {"username": "dave", "role": "intern"},
}


class CsvPolicyEnforcer:
    def __init__(self, policy_path: str | Path):
        self.policies: set[tuple[str, str, str]] = set()
        self.load_policy(policy_path)

    def load_policy(self, policy_path: str | Path) -> None:
        with open(policy_path, "r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = [part.strip() for part in line.split(",")]
                if len(parts) == 4 and parts[0] == "p":
                    self.policies.add((parts[1], parts[2], parts[3]))

    def enforce(self, role: str, resource: str, action: str) -> bool:
        if role == "admin":
            return True
        return (role, resource, action) in self.policies


POLICY_PATH = Path(__file__).with_name("policy.csv")
enforcer = CsvPolicyEnforcer(POLICY_PATH)


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ", 1)[1].strip()
    user = MOCK_USERS.get(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user


def require_permission(resource: str, action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=401, detail="Missing current user")

            role = current_user["role"]
            allowed = enforcer.enforce(role, resource, action)

            if not allowed:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role '{role}' cannot '{action}' on '{resource}'",
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator
