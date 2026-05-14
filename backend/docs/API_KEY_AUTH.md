# API Key Authentication System for Axion-Pilot

## Overview

Axion-Pilot now supports programmatic API key authentication alongside traditional JWT. This enables:

- **Programmatic Access**: Server-to-server integrations, CI/CD pipelines, ML workflows
- **Scope-Based Authorization**: Fine-grained permissions (read, write, delete, admin)
- **Rate Limiting**: Per-key requests-per-minute limits with Redis tracking
- **Audit Trail**: Track which API keys accessed what, when

---

## Quick Start

### 1. Create an API Key

```bash
curl -X POST https://api.axion-pilot.com/api/v1/api_keys \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ml-pipeline",
    "scopes": ["read:projects", "write:projects"],
    "rate_limit_rpm": 500
  }'
```

**Response** (full key shown **once only**):
```json
{
  "id": "key-uuid-123",
  "full_key": "sk_axion_abc123def456ghi789jkl012mno345pqr678",
  "name": "ml-pipeline",
  "key_prefix": "sk_axion_abc1",
  "scopes": ["read:projects", "write:projects"],
  "rate_limit_rpm": 500,
  "created_at": "2026-05-14T12:00:00Z",
  "expires_at": null
}
```

**⚠️ IMPORTANT**: Store the `full_key` securely (e.g., in a secrets manager). It won't be shown again.

### 2. Use the API Key

```bash
curl -X GET https://api.axion-pilot.com/api/v1/projects \
  -H "Authorization: Bearer sk_axion_abc123def456ghi789jkl012mno345pqr678"
```

**Response includes rate limit headers**:
```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 499
X-RateLimit-Reset: 2026-05-14T12:01:00Z
```

### 3. Hit Rate Limit

After 500 requests in a minute:

```bash
curl -X GET https://api.axion-pilot.com/api/v1/projects \
  -H "Authorization: Bearer sk_axion_abc123..."
```

**Response (429)**:
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Limit: 500 requests per minute.",
  "limit": 500,
  "remaining": 0,
  "reset_at": "2026-05-14T12:01:30Z"
}

Headers:
  HTTP/1.1 429 Too Many Requests
  X-RateLimit-Limit: 500
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 2026-05-14T12:01:30Z
  Retry-After: 30
```

---

## API Endpoints

### POST /api/v1/api_keys — Create a new API key

```bash
curl -X POST https://api.axion-pilot.com/api/v1/api_keys \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "data-sync",
    "scopes": ["read:projects"],
    "rate_limit_rpm": 1000,
    "expires_at": "2027-05-14T00:00:00Z"  # Optional
  }'
```

**Parameters**:
- `name` (string, required): Human-readable name for the key
- `scopes` (array, optional): List of permissions (default: `["read:projects"]`)
- `rate_limit_rpm` (integer, optional): Requests per minute (default: 1000, max: 100000)
- `expires_at` (datetime, optional): Expiration date (if omitted, never expires)

**Response**: `201 Created` with full key (shown once only)

---

### GET /api/v1/api_keys — List API keys

```bash
curl -X GET https://api.axion-pilot.com/api/v1/api_keys \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Query parameters**:
- `active_only` (boolean, optional): Filter to active keys only (default: false)

**Response**:
```json
{
  "items": [
    {
      "id": "key-uuid-123",
      "name": "ml-pipeline",
      "key_prefix": "sk_axion_abc1",
      "scopes": ["read:projects", "write:projects"],
      "rate_limit_rpm": 500,
      "created_at": "2026-05-14T12:00:00Z",
      "last_used_at": "2026-05-14T12:30:15Z",
      "expires_at": null,
      "active": true
    }
  ],
  "total": 1
}
```

**Note**: Only the key prefix is shown (never the full key again).

---

### PATCH /api/v1/api_keys/{key_id} — Update an API key

```bash
curl -X PATCH https://api.axion-pilot.com/api/v1/api_keys/key-uuid-123 \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ml-pipeline-v2",
    "scopes": ["read:projects", "write:projects", "read:usage"],
    "rate_limit_rpm": 750,
    "active": true
  }'
```

**Updatable fields**:
- `name`: Change the key's display name
- `scopes`: Update permissions
- `rate_limit_rpm`: Adjust rate limit
- `expires_at`: Extend or shorten expiration
- `active`: Enable/disable without deleting

---

### DELETE /api/v1/api_keys/{key_id} — Revoke an API key

```bash
curl -X DELETE https://api.axion-pilot.com/api/v1/api_keys/key-uuid-123 \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Response**: `204 No Content`

**Note**: This is a soft delete (sets `active=false`). The key record is retained for audit purposes.

---

### POST /api/v1/api_keys/{key_id}/rotate — Rotate an API key

```bash
curl -X POST https://api.axion-pilot.com/api/v1/api_keys/key-uuid-123/rotate \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Response**: `200 OK` with both old (now inactive) and new keys

```json
{
  "old_key": {
    "id": "key-uuid-123",
    "name": "ml-pipeline",
    "key_prefix": "sk_axion_abc1",
    "active": false,
    ...
  },
  "new_key": {
    "id": "key-uuid-456",
    "full_key": "sk_axion_xyz789...",
    "name": "ml-pipeline (rotated)",
    "key_prefix": "sk_axion_xyz7",
    ...
  },
  "message": "Key rotated successfully. Old key deprecated."
}
```

---

## Scopes System

### Available Scopes

| Scope | Description |
|-------|-------------|
| `read:projects` | Read project information and list projects |
| `write:projects` | Create and modify projects |
| `delete:projects` | Delete projects |
| `read:usage` | Read API usage and billing information |
| `admin:org` | Full administrative access (implies all other scopes) |

### Scope Validation

Every API request validates that the key has the required scope:

```bash
# ✅ This works (has read:projects scope)
curl -X GET https://api.axion-pilot.com/api/v1/projects \
  -H "Authorization: Bearer sk_axion_abc123..." \
  -H "Scopes: read:projects"

# ❌ This fails (missing delete:projects scope)
curl -X DELETE https://api.axion-pilot.com/api/v1/projects/123 \
  -H "Authorization: Bearer sk_axion_abc123..." \
  -H "Scopes: read:projects"
```

**Response (403)**:
```json
{
  "detail": "Insufficient permissions. Required scope(s): delete:projects"
}
```

### Scope Hierarchy

- `admin:org` implies all other scopes
- Other scopes are independent (having `read:projects` does NOT grant `write:projects`)

---

## Key Generation Algorithm

### How Keys Are Generated

1. **Prefix**: Fixed `sk_axion_` (8 characters)
2. **Random**: 40 cryptographically random characters (alphanumeric)
3. **Total**: 48 characters (24 bytes of entropy)

**Example**: `sk_axion_AbCd1EfG2HiJ3KlM4NoP5QrS6TuV7WxY8Z`

### Key Storage

- **Full key**: Shown to user **once only** on creation, then discarded
- **Prefix** (12 chars): Stored in DB for efficient lookup (`sk_axion_AbCd`)
- **Hash**: Bcrypt hash of full key stored in DB

**Why this design?**
- Bcrypt is one-way, making it impossible to recover the full key from storage
- Even if DB is compromised, attackers cannot retrieve working keys
- Prefix provides fast DB lookup without storing plaintext keys
- Matches industry standards (Stripe, GitHub, etc.)

---

## Rate Limiting

### How It Works

- **Window**: Per-minute sliding window (resets every 60 seconds)
- **Storage**: Redis (primary) with PostgreSQL fallback
- **Enforcement**: Returns `429 Too Many Requests` when exceeded

### Rate Limit Headers

Every response includes three headers (if API key used):

```
X-RateLimit-Limit: 500              # Max requests per minute
X-RateLimit-Remaining: 375          # Requests left before limit
X-RateLimit-Reset: 2026-05-14T12:01:00Z  # When limit resets (ISO 8601)
```

### Example: Rate Limit Flow

```bash
# Request 1-500: Success with decreasing X-RateLimit-Remaining
for i in {1..500}; do
  curl -s -X GET https://api.axion-pilot.com/api/v1/projects \
    -H "Authorization: Bearer sk_axion_abc123..." \
    | jq '.data | length'  # Request succeeds
done

# Request 501: Rate limited
curl -X GET https://api.axion-pilot.com/api/v1/projects \
  -H "Authorization: Bearer sk_axion_abc123..."

# Response (429)
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Limit: 500 requests per minute.",
  "remaining": 0,
  "reset_at": "2026-05-14T12:01:30Z"
}
```

### Adjusting Rate Limits

Update the `rate_limit_rpm` for an API key:

```bash
curl -X PATCH https://api.axion-pilot.com/api/v1/api_keys/key-uuid-123 \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rate_limit_rpm": 2000}'
```

---

## Security Best Practices

### 1. **Rotate Keys Periodically**

Use the rotate endpoint to generate new keys:

```bash
curl -X POST https://api.axion-pilot.com/api/v1/api_keys/key-uuid-123/rotate \
  -H "Authorization: Bearer $JWT_TOKEN"
```

This creates a new key and deprecates the old one, giving time to transition.

### 2. **Minimize Scopes**

Only grant the scopes your integration needs:

```json
{
  "name": "read-only-integration",
  "scopes": ["read:projects"],  // ✅ Only read
  "rate_limit_rpm": 100
}
```

Instead of:

```json
{
  "scopes": ["read:projects", "write:projects", "delete:projects", "admin:org"]  // ❌ Overprivileged
}
```

### 3. **Set Expiration Dates**

Limit key lifetime:

```bash
curl -X POST https://api.axion-pilot.com/api/v1/api_keys \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "temporary-migration",
    "scopes": ["read:projects", "write:projects"],
    "expires_at": "2026-06-14T00:00:00Z"  // Expires in 1 month
  }'
```

### 4. **Store Keys Securely**

- Use environment variables or secrets managers (AWS Secrets Manager, HashiCorp Vault, etc.)
- Never commit keys to version control
- Rotate keys if accidentally exposed

### 5. **Monitor Usage**

Review `last_used_at` timestamps to detect stale keys:

```bash
curl -X GET https://api.axion-pilot.com/api/v1/api_keys?active_only=true \
  -H "Authorization: Bearer $JWT_TOKEN" \
  | jq '.items[] | select(.last_used_at < "2026-03-14T00:00:00Z")'  # Unused for 2 months
```

---

## Troubleshooting

### 401 Unauthorized

**Cause**: Invalid, expired, inactive, or malformed API key

```json
{
  "detail": "API key not found or inactive"
}
```

**Solution**:
1. Verify key prefix matches: `sk_axion_XXXX`
2. Check if key is active: `curl -X GET .../api_keys` and look for `"active": true`
3. Check expiration: Compare `expires_at` to current time
4. Regenerate key if necessary

---

### 403 Forbidden

**Cause**: API key lacks required scope

```json
{
  "detail": "Insufficient permissions. Required scope: delete:projects"
}
```

**Solution**:
1. Check required scopes for endpoint (see API documentation)
2. Update key scopes: `curl -X PATCH .../api_keys/{key_id} -d '{"scopes": ["delete:projects", ...]}'`
3. Or rotate and create new key with correct scopes

---

### 429 Too Many Requests

**Cause**: Rate limit exceeded

```json
{
  "error": "Too Many Requests",
  "remaining": 0,
  "reset_at": "2026-05-14T12:01:30Z"
}
```

**Solution**:
1. Wait for reset time or check Retry-After header
2. Implement exponential backoff in your client
3. Request rate limit increase: Update `rate_limit_rpm` (if you have permission)
4. Contact support for quota increase

---

### 500 Internal Server Error

**Cause**: Server error (usually transient)

**Solution**:
1. Check Redis/database connection status
2. Wait 30 seconds and retry with exponential backoff
3. Contact support if persists

---

## Example Implementations

### Python

```python
import requests
import time

API_KEY = "sk_axion_abc123def456ghi789jkl012mno345pqr678"
BASE_URL = "https://api.axion-pilot.com/api/v1"

def get_projects():
    """List projects with rate limit handling."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    response = requests.get(f"{BASE_URL}/projects", headers=headers)
    
    # Check rate limit headers
    limit = response.headers.get("X-RateLimit-Limit")
    remaining = response.headers.get("X-RateLimit-Remaining")
    reset = response.headers.get("X-RateLimit-Reset")
    
    print(f"Requests remaining: {remaining}/{limit}")
    print(f"Reset at: {reset}")
    
    if response.status_code == 429:
        print(f"Rate limited. Retry after {response.headers.get('Retry-After')} seconds")
        return None
    
    return response.json()

def create_project_with_retry(data, max_retries=3):
    """Create project with exponential backoff."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    
    for attempt in range(max_retries):
        response = requests.post(
            f"{BASE_URL}/projects",
            headers=headers,
            json=data,
        )
        
        if response.status_code == 429:
            wait_time = int(response.headers.get("Retry-After", 2 ** attempt))
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue
        
        if response.status_code >= 400:
            print(f"Error: {response.json()}")
            return None
        
        return response.json()
    
    print("Max retries exceeded")
    return None

# Usage
projects = get_projects()
if projects:
    print(f"Found {len(projects)} projects")

# Create project with retry
new_project = create_project_with_retry({"name": "test-project"})
```

### Node.js / JavaScript

```javascript
const API_KEY = "sk_axion_abc123def456ghi789jkl012mno345pqr678";
const BASE_URL = "https://api.axion-pilot.com/api/v1";

async function getProjects() {
  const response = await fetch(`${BASE_URL}/projects`, {
    headers: {
      Authorization: `Bearer ${API_KEY}`,
    },
  });

  // Check rate limit headers
  const limit = response.headers.get("X-RateLimit-Limit");
  const remaining = response.headers.get("X-RateLimit-Remaining");
  const reset = response.headers.get("X-RateLimit-Reset");

  console.log(`Requests remaining: ${remaining}/${limit}`);
  console.log(`Reset at: ${reset}`);

  if (response.status === 429) {
    const retryAfter = response.headers.get("Retry-After");
    console.log(`Rate limited. Retry after ${retryAfter} seconds`);
    return null;
  }

  return response.json();
}

async function createProjectWithRetry(data, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const response = await fetch(`${BASE_URL}/projects`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get("Retry-After") || 2 ** attempt);
      console.log(`Rate limited. Waiting ${retryAfter}s...`);
      await new Promise((resolve) => setTimeout(resolve, retryAfter * 1000));
      continue;
    }

    if (!response.ok) {
      console.error(`Error: ${response.statusText}`);
      return null;
    }

    return response.json();
  }

  console.log("Max retries exceeded");
  return null;
}

// Usage
const projects = await getProjects();
if (projects) {
  console.log(`Found ${projects.length} projects`);
}

const newProject = await createProjectWithRetry({ name: "test-project" });
```

### cURL

```bash
#!/bin/bash

API_KEY="sk_axion_abc123def456ghi789jkl012mno345pqr678"
BASE_URL="https://api.axion-pilot.com/api/v1"

# Function to handle rate limiting with retry
function api_call_with_retry() {
    local method=$1
    local endpoint=$2
    local data=$3
    local max_retries=3
    
    for ((attempt=1; attempt<=max_retries; attempt++)); do
        if [ -z "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                "$BASE_URL$endpoint" \
                -H "Authorization: Bearer $API_KEY")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                "$BASE_URL$endpoint" \
                -H "Authorization: Bearer $API_KEY" \
                -H "Content-Type: application/json" \
                -d "$data")
        fi
        
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n-1)
        
        if [ "$http_code" = "429" ]; then
            retry_after=$(echo "$body" | jq -r '.reset_at')
            echo "Rate limited. Reset at: $retry_after"
            sleep 2
            continue
        fi
        
        echo "$body"
        return 0
    done
    
    echo "Max retries exceeded"
    return 1
}

# List projects
api_call_with_retry "GET" "/projects"

# Create project
api_call_with_retry "POST" "/projects" '{
    "name": "Test Project",
    "description": "Created via API key"
}'
```

---

## Migration from JWT to API Key

If you're currently using JWT and want to switch to API keys:

### 1. Create an API key for your integration

```bash
curl -X POST https://api.axion-pilot.com/api/v1/api_keys \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "name": "migration-key",
    "scopes": ["read:projects", "write:projects"],
    "rate_limit_rpm": 1000
  }'
```

### 2. Update your code to use API key

**Before (JWT)**:
```python
headers = {"Authorization": f"Bearer {jwt_token}"}
```

**After (API Key)**:
```python
headers = {"Authorization": f"Bearer {api_key}"}
```

### 3. Test the new API key

```bash
curl -X GET https://api.axion-pilot.com/api/v1/projects \
  -H "Authorization: Bearer sk_axion_abc123..."
```

### 4. Verify it works end-to-end

Test in your staging environment first before production deployment.

### 5. Rotate the old JWT

Once migrated, you can invalidate the old JWT by rotating your token version in your user account settings.

---

## Advanced Topics

### Custom Rate Limits

By default, API keys have a 1000 requests/minute limit. Request higher limits by contacting support with:

- Use case (e.g., "Data sync for 10k+ records/day")
- Expected request volume
- Integration requirements

### Webhook Integration

API keys can be used to secure webhook endpoints (coming soon):

```bash
curl -X POST https://your-webhook.example.com/inbound \
  -H "Authorization: Bearer sk_axion_abc123..." \
  -H "Content-Type: application/json" \
  -d '{"event": "project.created", ...}'
```

### Analytics & Monitoring

View API key usage in your org dashboard (coming soon):

```bash
curl -X GET https://api.axion-pilot.com/api/v1/analytics/api_keys \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

## Support

- **Documentation**: https://docs.axion-pilot.com/api-keys
- **GitHub Issues**: https://github.com/axion-pilot/issues
- **Email**: support@axion-pilot.com
- **Status**: https://status.axion-pilot.com
