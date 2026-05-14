"""Scope validation for API key permissions."""

from typing import List, Union
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials

# Define all available scopes in the system
VALID_SCOPES = {
    "read:projects": "Read project information and details",
    "write:projects": "Create and update projects",
    "delete:projects": "Delete projects",
    "read:usage": "Read API usage and billing information",
    "admin:org": "Full administrative access to organization",
}

SCOPE_HIERARCHY = {
    # admin:org implies all other scopes
    "admin:org": [
        "read:projects", "write:projects", "delete:projects", "read:usage"
    ]
}


def validate_scope(scope: str) -> bool:
    """Check if a scope is valid."""
    return scope in VALID_SCOPES


def validate_scopes(scopes: List[str]) -> bool:
    """Check if all scopes in a list are valid."""
    return all(validate_scope(scope) for scope in scopes)


def check_scopes(user_scopes: List[str], required_scopes: Union[str, List[str]]) -> bool:
    """
    Check if user has required scope(s).
    
    Respects scope hierarchy (admin:org implies all others).
    
    Args:
        user_scopes: List of scopes the user has (from API key or JWT)
        required_scopes: Single scope or list of scopes required
    
    Returns:
        True if user has required scope(s), False otherwise
    
    Example:
        user_scopes = ["read:projects", "write:projects"]
        check_scopes(user_scopes, "read:projects")  # True
        check_scopes(user_scopes, "delete:projects")  # False
        check_scopes(user_scopes, ["read:projects", "write:projects"])  # True
    """
    if isinstance(required_scopes, str):
        required_scopes = [required_scopes]
    
    # Check if user has admin scope (implies all)
    if "admin:org" in user_scopes:
        return True
    
    # Check if user has any of the required scopes
    return any(scope in user_scopes for scope in required_scopes)


def require_scope(required_scopes: Union[str, List[str]]):
    """
    FastAPI dependency for scope validation.
    
    Use in route dependencies to enforce scope requirements.
    
    Args:
        required_scopes: Single scope or list of required scopes
    
    Raises:
        HTTPException (403): If required scopes are missing
    
    Example:
        @router.get("/projects", dependencies=[Depends(require_scope("read:projects"))])
        def list_projects():
            ...
        
        # Or with multiple scopes (user must have at least one):
        @router.delete("/projects/{id}", dependencies=[Depends(require_scope(["delete:projects", "admin:org"]))])
        def delete_project(id: str):
            ...
    """
    async def scope_dependency(request_scopes: List[str] = None) -> None:
        """Inner dependency function."""
        if not request_scopes:
            request_scopes = []
        
        if not check_scopes(request_scopes, required_scopes):
            required_str = required_scopes if isinstance(required_scopes, str) else ", ".join(required_scopes)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scope(s): {required_str}",
            )
    
    return scope_dependency


def get_scope_description(scope: str) -> str:
    """Get human-readable description of a scope."""
    return VALID_SCOPES.get(scope, "Unknown scope")


def format_scopes_for_display(scopes: List[str]) -> str:
    """Format a list of scopes for display."""
    return ", ".join(f"'{scope}'" for scope in scopes)
