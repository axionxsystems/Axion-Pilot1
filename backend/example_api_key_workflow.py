#!/usr/bin/env python3
"""
Complete API Key Workflow Example
==================================

This script demonstrates the full lifecycle of API keys:
1. Creating an API key
2. Using it to make requests
3. Handling rate limits
4. Rotating keys
5. Revoking keys

Usage:
    python3 example_api_key_workflow.py <JWT_TOKEN>

Example:
    python3 example_api_key_workflow.py "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
"""

import sys
import json
import time
import requests
from datetime import datetime, timedelta


class AxionAPIClient:
    """Client for Axion-Pilot API key management."""
    
    def __init__(self, base_url="http://localhost:8000", jwt_token=None, api_key=None):
        self.base_url = base_url.rstrip("/")
        self.jwt_token = jwt_token
        self.api_key = api_key
        self.session = requests.Session()
    
    def _get_auth_header(self):
        """Get Authorization header."""
        token = self.api_key or self.jwt_token
        if not token:
            raise ValueError("No JWT token or API key provided")
        return {"Authorization": f"Bearer {token}"}
    
    def _handle_response(self, response, method, endpoint):
        """Handle response and print rate limit info."""
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        # Print rate limit headers if present
        if "X-RateLimit-Limit" in response.headers:
            print(f"Rate Limit: {response.headers.get('X-RateLimit-Limit')} req/min")
            print(f"Remaining: {response.headers.get('X-RateLimit-Remaining')}")
            print(f"Reset: {response.headers.get('X-RateLimit-Reset')}")
        
        if response.status_code >= 400:
            print(f"Error: {response.text}")
            return None
        
        return response.json()
    
    def create_api_key(self, name, scopes=None, rate_limit_rpm=500, expires_at=None):
        """Create a new API key."""
        if scopes is None:
            scopes = ["read:projects", "write:projects"]
        
        url = f"{self.base_url}/api/v1/api_keys"
        headers = self._get_auth_header()
        
        payload = {
            "name": name,
            "scopes": scopes,
            "rate_limit_rpm": rate_limit_rpm,
        }
        
        if expires_at:
            payload["expires_at"] = expires_at.isoformat()
        
        response = self.session.post(url, json=payload, headers=headers)
        return self._handle_response(response, "POST", "/api/v1/api_keys")
    
    def list_api_keys(self):
        """List all API keys."""
        url = f"{self.base_url}/api/v1/api_keys"
        headers = self._get_auth_header()
        
        response = self.session.get(url, headers=headers)
        return self._handle_response(response, "GET", "/api/v1/api_keys")
    
    def update_api_key(self, key_id, **kwargs):
        """Update an API key."""
        url = f"{self.base_url}/api/v1/api_keys/{key_id}"
        headers = self._get_auth_header()
        
        response = self.session.patch(url, json=kwargs, headers=headers)
        return self._handle_response(response, "PATCH", f"/api/v1/api_keys/{key_id}")
    
    def rotate_api_key(self, key_id):
        """Rotate an API key."""
        url = f"{self.base_url}/api/v1/api_keys/{key_id}/rotate"
        headers = self._get_auth_header()
        
        response = self.session.post(url, headers=headers)
        return self._handle_response(response, "POST", f"/api/v1/api_keys/{key_id}/rotate")
    
    def delete_api_key(self, key_id):
        """Delete (revoke) an API key."""
        url = f"{self.base_url}/api/v1/api_keys/{key_id}"
        headers = self._get_auth_header()
        
        response = self.session.delete(url, headers=headers)
        print(f"\nDELETE /api/v1/api_keys/{key_id}")
        print(f"Status: {response.status_code}")
        return response.status_code == 204
    
    def list_projects(self):
        """List projects using API key or JWT."""
        url = f"{self.base_url}/api/v1/projects"
        headers = self._get_auth_header()
        
        response = self.session.get(url, headers=headers)
        return self._handle_response(response, "GET", "/api/v1/projects")


def main():
    """Run the complete workflow."""
    
    if len(sys.argv) < 2:
        print("Usage: python3 example_api_key_workflow.py <JWT_TOKEN>")
        print("\nExample with localhost:")
        print("  JWT_TOKEN='eyJ...' python3 example_api_key_workflow.py $JWT_TOKEN")
        sys.exit(1)
    
    jwt_token = sys.argv[1]
    base_url = "http://localhost:8000"
    
    print("=" * 80)
    print("AXION-PILOT API KEY WORKFLOW EXAMPLE")
    print("=" * 80)
    
    # Step 1: Create client with JWT
    print("\n[STEP 1] Initialize client with JWT token")
    client = AxionAPIClient(base_url=base_url, jwt_token=jwt_token)
    print("✓ Client initialized")
    
    # Step 2: Create an API key
    print("\n[STEP 2] Create a new API key")
    expires_at = datetime.utcnow() + timedelta(days=30)
    api_key_response = client.create_api_key(
        name="demo-integration",
        scopes=["read:projects", "write:projects"],
        rate_limit_rpm=100,
        expires_at=expires_at,
    )
    
    if not api_key_response:
        print("❌ Failed to create API key")
        sys.exit(1)
    
    full_key = api_key_response["full_key"]
    key_id = api_key_response["id"]
    print(f"✓ API key created!")
    print(f"  ID: {key_id}")
    print(f"  Full Key: {full_key}")
    print(f"  Prefix: {api_key_response['key_prefix']}")
    print(f"  Rate Limit: {api_key_response['rate_limit_rpm']} req/min")
    print(f"  ⚠️  Store the full key securely. It won't be shown again!")
    
    # Step 3: List API keys (should show prefix only)
    print("\n[STEP 3] List API keys (shows prefix only)")
    list_response = client.list_api_keys()
    if list_response and list_response["items"]:
        key = list_response["items"][0]
        print(f"✓ Listed {list_response['total']} key(s)")
        print(f"  Name: {key['name']}")
        print(f"  Prefix: {key['key_prefix']}")
        print(f"  Active: {key['active']}")
    
    # Step 4: Switch to API key auth
    print("\n[STEP 4] Switch to API key authentication")
    client.api_key = full_key
    client.jwt_token = None
    print(f"✓ Using API key: {full_key[:20]}...")
    
    # Step 5: Make a request with API key
    print("\n[STEP 5] Make a request using API key")
    projects = client.list_projects()
    print(f"✓ Request successful!")
    if projects:
        print(f"  Found {len(projects) if isinstance(projects, list) else len(projects.get('items', []))} projects")
    
    # Step 6: Stress test to hit rate limit
    print("\n[STEP 6] Stress test to demonstrate rate limiting")
    print(f"Making 105 requests with rate limit of 100 req/min...")
    
    for i in range(1, 106):
        response = requests.get(
            f"{base_url}/api/v1/projects",
            headers={"Authorization": f"Bearer {full_key}"}
        )
        
        remaining = response.headers.get("X-RateLimit-Remaining", "?")
        
        if response.status_code == 429:
            print(f"  Request {i}: 429 Rate Limited")
            print(f"  Reset: {response.headers.get('X-RateLimit-Reset')}")
            break
        elif i % 25 == 0:
            print(f"  Request {i}: 200 OK (Remaining: {remaining})")
        
        time.sleep(0.01)  # Small delay to avoid overwhelming
    
    # Step 7: Update API key
    print("\n[STEP 7] Update API key (increase rate limit)")
    client.api_key = None
    client.jwt_token = jwt_token
    updated = client.update_api_key(
        key_id,
        rate_limit_rpm=500,
        name="demo-integration-v2",
    )
    if updated:
        print(f"✓ API key updated!")
        print(f"  New rate limit: {updated['rate_limit_rpm']} req/min")
    
    # Step 8: Rotate API key
    print("\n[STEP 8] Rotate API key")
    rotate_response = client.rotate_api_key(key_id)
    if rotate_response:
        old_key = rotate_response["old_key"]
        new_key = rotate_response["new_key"]
        print(f"✓ API key rotated!")
        print(f"  Old key (deprecated): {old_key['key_prefix']} - Active: {old_key['active']}")
        print(f"  New key: {new_key['key_prefix']}")
        print(f"  New full key: {new_key['full_key']}")
        
        # Update our client with new key
        full_key = new_key["full_key"]
        new_key_id = new_key["id"]
    
    # Step 9: Delete API key
    print("\n[STEP 9] Delete (revoke) the first API key")
    if client.delete_api_key(key_id):
        print(f"✓ API key revoked!")
    
    # Step 10: Verify key is gone
    print("\n[STEP 10] Verify revoked key is inactive")
    list_response = client.list_api_keys()
    if list_response:
        active_keys = [k for k in list_response["items"] if k["active"]]
        print(f"✓ Active keys: {len(active_keys)}")
    
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE")
    print("=" * 80)
    print("\nSummary:")
    print(f"  Created API key: {key_id}")
    print(f"  Rotated to: {new_key_id}")
    print(f"  Revoked old key")
    print(f"\nNext steps:")
    print(f"  1. Store your API keys in a secure secrets manager")
    print(f"  2. Use the key in your integrations")
    print(f"  3. Monitor key usage and rotate regularly")
    print(f"  4. Set expiration dates for keys")


if __name__ == "__main__":
    main()
