# 🎯 COPILOT PROMPTS FOR AXION SCALING
## Copy-Paste Ready Prompts for VS Code

---

## ✅ PROMPT 1: PostgreSQL Migration & Alembic Setup

```
You are a FastAPI + SQLAlchemy expert. I'm migrating from SQLite to PostgreSQL 
and need to create Alembic migrations for a SaaS platform.

Current location: /backend/alembic/versions/

Create comprehensive Alembic migration files that add these new tables 
and relationships to the existing schema:

NEW TABLES TO ADD:

1. organizations (B2B support)
   - id: UUID primary key
   - name: String(255), not null
   - slug: String(100), unique, not null
   - plan: Enum('free', 'starter', 'pro', 'enterprise')
   - monthly_cost: Integer (in cents)
   - api_calls_limit: Integer (monthly limit)
   - created_at: DateTime default now
   - updated_at: DateTime
   - deleted_at: DateTime nullable (soft delete)

2. subscriptions (Stripe integration)
   - id: UUID
   - organization_id: FK to organizations
   - stripe_subscription_id: String unique
   - stripe_customer_id: String unique
   - tier: Enum('free', 'starter', 'pro', 'enterprise')
   - monthly_cost: Integer (cents)
   - next_billing_date: DateTime
   - status: Enum('active', 'past_due', 'canceled', 'trialing')
   - created_at: DateTime
   - updated_at: DateTime

3. api_keys (Programmatic access)
   - id: UUID
   - organization_id: FK
   - name: String(100)
   - key_prefix: String(8) (for display)
   - key_hash: String(255) (bcrypt hashed)
   - scopes: JSON array ('read:projects', 'write:projects', 'admin')
   - rate_limit: Integer (requests per minute)
   - created_at: DateTime
   - expires_at: DateTime nullable
   - last_used_at: DateTime nullable
   - active: Boolean default true

4. usage (Metered billing)
   - id: UUID
   - organization_id: FK
   - api_calls: Integer default 0
   - documents_generated: Integer default 0
   - pages_processed: Integer default 0
   - storage_mb: Integer default 0
   - period_start: Date
   - period_end: Date
   - created_at: DateTime

5. audit_logs (Compliance)
   - id: UUID
   - organization_id: FK
   - actor_id: UUID (FK to users)
   - action: String (e.g., 'project_created', 'api_key_created')
   - resource_type: String (e.g., 'project', 'user')
   - resource_id: UUID
   - changes: JSON (what changed)
   - ip_address: String
   - user_agent: String
   - timestamp: DateTime
   - status: Enum('success', 'failure')

6. templates (Custom templates)
   - id: UUID
   - organization_id: FK nullable (NULL = public)
   - name: String(255)
   - category: String(50)
   - description: Text
   - content: Text (template structure)
   - variables: JSON (list of required variables)
   - is_public: Boolean
   - created_by: FK to users
   - created_at: DateTime
   - updated_at: DateTime

7. webhooks (Event delivery)
   - id: UUID
   - organization_id: FK
   - url: String
   - events: JSON array (['project.created', 'project.completed'])
   - secret: String (for HMAC validation)
   - active: Boolean
   - created_at: DateTime
   - created_by: FK to users

8. webhook_deliveries (Retry tracking)
   - id: UUID
   - webhook_id: FK
   - payload: JSON
   - status_code: Integer
   - response: Text
   - attempts: Integer
   - next_retry: DateTime
   - created_at: DateTime

REQUIREMENTS:
1. Use UUID primary keys (uuid.uuid4)
2. Add proper indexes on:
   - organization_id (all tables)
   - created_at (for sorting)
   - stripe_subscription_id (subscriptions)
   - key_hash (api_keys)
   - period_start (usage)
3. Add foreign key constraints with CASCADE delete where appropriate
4. Add CHECK constraints for enum fields
5. Make created_at and updated_at standard on all tables
6. Generate up() and down() functions
7. Add comments explaining each field
8. Ensure backward compatibility (don't break existing tables)

Generate the migration file(s) in Alembic format, ready to run with:
'alembic upgrade head'
```

---

## ✅ PROMPT 2: FastAPI API v1 Restructuring

```
I'm restructuring my FastAPI backend to support API versioning and B2B features.

Current location: /backend/app/api/

REQUIREMENTS:
1. Move all routes to /api/v1/ prefix
2. Create service layer for business logic
3. Add comprehensive error handling
4. Implement request/response logging middleware
5. Add rate limiting middleware
6. Setup proper OpenAPI documentation

NEW STRUCTURE:
/app/api/v1/
  __init__.py
  /projects/
    __init__.py
    routes.py (existing project endpoints)
  /organizations/
    __init__.py
    routes.py (NEW - CRUD for orgs)
  /subscriptions/
    __init__.py
    routes.py (NEW - Stripe integration)
  /webhooks/
    __init__.py
    routes.py (NEW - webhook management)
  /api_keys/
    __init__.py
    routes.py (NEW - API key management)
  /analytics/
    __init__.py
    routes.py (NEW - usage analytics)
  /templates/
    __init__.py
    routes.py (NEW - template management)

/app/services/
  __init__.py
  project_service.py (move logic here)
  organization_service.py (NEW)
  subscription_service.py (NEW)
  webhook_service.py (NEW)
  api_key_service.py (NEW)

/app/middleware/
  __init__.py
  logging.py (request/response logging)
  rate_limit.py (rate limiting per API key)
  usage_tracking.py (track API usage)
  error_handler.py (global error handling)

Generate:
1. Updated app/main.py that imports from /api/v1/
2. Middleware implementations
3. Base routes for each module (with example endpoints)
4. Proper error response schemas
5. OpenAPI tags for documentation

FEATURES TO INCLUDE:
- Proper HTTP status codes (200, 201, 400, 401, 403, 404, 429, 500)
- Consistent error response format:
  {
    "error": "error_code",
    "message": "Human readable message",
    "status": 400,
    "timestamp": "2024-01-15T10:30:00Z"
  }
- Request ID tracking for debugging
- Correlation ID for distributed tracing
- API versioning in response headers
```

---

## ✅ PROMPT 3: Enterprise Authentication System

```
I need to implement enterprise-grade authentication in my FastAPI app.

Current location: /backend/app/auth/

Build a multi-authentication system supporting:
1. JWT (existing - keep as is)
2. API Key authentication (NEW)
3. OAuth 2.0 with Auth0 (NEW)
4. SAML 2.0 for enterprises (NEW)
5. MFA/TOTP (NEW)

STRUCTURE:
/app/auth/
  __init__.py
  jwt_handler.py (REFACTOR - keep existing)
  api_key_handler.py (NEW)
  oauth_handler.py (NEW - Auth0)
  saml_handler.py (NEW)
  mfa_handler.py (NEW)
  permissions.py (scope-based)
  schemas.py (Pydantic models)

REQUIREMENTS:

1. API KEY AUTHENTICATION:
   - Header: "X-API-Key: sk_live_abc123..."
   - Support key rotation
   - Implement scopes: 'read:projects', 'write:projects', 'admin'
   - Rate limiting per API key
   - Key expiration dates

2. OAUTH 2.0 (Auth0):
   - Support authorization_code flow
   - Token refresh mechanism
   - PKCE for web apps
   - Organization separation via Auth0 orgs

3. SAML 2.0:
   - Support metadata URL import
   - Assertion signing verification
   - NameID mapping to organization
   - Attribute mapping for roles

4. MFA:
   - TOTP (Google Authenticator, Authy)
   - Backup codes
   - Phone SMS (Twilio integration ready)

5. SCOPE-BASED PERMISSIONS:
   - read:projects, write:projects, delete:projects
   - read:organizations, admin:organizations
   - read:api_keys, write:api_keys, admin:api_keys
   - read:webhooks, admin:webhooks
   - read:templates, write:templates, admin:templates

GENERATE:
1. Dependency injection for each auth method
2. Middleware to extract auth method and validate
3. Permission checking decorators
4. OAuth2 scheme definitions for Swagger
5. Example implementations for each method
6. Tests/examples for each auth flow

SECURITY REQUIREMENTS:
- Never log secrets/tokens
- Hash all API keys with bcrypt
- Implement rate limiting on token generation
- CORS headers configuration
- CSRF protection if needed
- Secure session handling
```

---

## ✅ PROMPT 4: Multi-Tenancy Implementation

```
I need to implement database-level multi-tenancy for my SaaS.

Current state: Single-tenant application

BUILD:
1. Middleware to extract tenant (organization_id)
2. Database query filtering by tenant
3. Row-Level Security if using PostgreSQL
4. Tenant context injection
5. Validation that user has access to requested tenant

IMPLEMENTATION DETAILS:

1. TENANT EXTRACTION MIDDLEWARE:
   - From JWT 'org_id' claim
   - From API key's associated org
   - From subdomain (org.example.com)
   - From request header (X-Organization-ID)
   - Priority order: JWT > Header > Subdomain

2. QUERY FILTERING:
   - Automatically add "WHERE organization_id = ?" to all queries
   - SQLAlchemy event listener approach
   - ORM-level filtering in models

3. VALIDATION:
   - Check user belongs to requested org
   - Check API key belongs to requested org
   - Prevent cross-org data access
   - Admin exception (can see all orgs)

4. DATA ISOLATION:
   All these tables must filter by org_id:
   - users → has organization_id
   - projects → has organization_id
   - api_keys → has organization_id
   - webhooks → has organization_id
   - templates → has organization_id
   - audit_logs → has organization_id
   - usage → has organization_id
   - subscriptions → has organization_id

GENERATE:
1. TenantMiddleware class
2. TenantContext (thread-local or context var)
3. Database session with org filtering
4. Example ORM models with proper relationships
5. Validation functions
6. Error handling for unauthorized access
7. Testing examples

SECURITY:
- No data leakage between tenants
- Tenant context cleared after request
- Comprehensive audit logging
- Rate limiting per tenant
```

---

## ✅ PROMPT 5: Celery + Redis Async Task Queue

```
I need to implement async task processing with Celery + Redis.

Current issue: Document generation blocks API responses

BUILD:
1. Redis connection with pooling
2. Celery task definitions
3. Task status tracking
4. Retry logic with exponential backoff
5. Result persistence
6. Admin monitoring dashboard

TASKS TO IMPLEMENT:

HIGH PRIORITY (should return in <10s):
- validate_input
- process_simple_request

MEDIUM PRIORITY (async, track status):
- generate_pdf
- generate_ppt
- generate_docx
- send_email

LOW PRIORITY (background):
- generate_analytics_report
- cleanup_old_files
- sync_stripe_data
- process_webhook_deliveries

CELERY CONFIGURATION:
/app/celery_app.py (NEW)
- Redis connection URI (use env vars)
- Task serialization (JSON)
- Result backend (PostgreSQL or Redis)
- Task routing by priority
- Time limits and soft limits
- Retry policy: exponential backoff, max 5 attempts
- Eta (scheduled execution)

GENERATE:
1. celery_app.py with configuration
2. tasks.py with all task definitions
3. Result models for tracking
4. Status endpoint to check task progress
5. Webhook delivery retry logic
6. Admin endpoint for queue monitoring
7. Docker Compose for local Redis
8. Example usage in routes
9. Monitoring/observability integration

TASK SIGNATURE:
@celery_app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    rate_limit='100/m',
    time_limit=600
)
def generate_document(self, org_id, project_id, format):
    ...

RESULT SCHEMA:
{
    "task_id": "uuid",
    "status": "pending|processing|completed|failed|retry",
    "progress": 45,
    "result": {...},
    "error": null,
    "created_at": "2024-01-15T10:00:00Z",
    "completed_at": null
}

API ENDPOINTS:
POST /api/v1/projects/{id}/generate-async
  → Returns task_id

GET /api/v1/tasks/{task_id}
  → Returns task status and progress

GET /api/v1/tasks/{task_id}/result
  → Returns final result when complete
```

---

## ✅ PROMPT 6: Stripe Billing & Usage Metering

```
I need to implement Stripe subscription + usage-based billing.

BUILD:
1. Stripe subscription management
2. Metered billing (usage per API call)
3. Invoice generation
4. Usage tracking
5. Billing dashboard

STRIPE SETUP:
- Subscription products for tiers (free, starter, pro, enterprise)
- Metering for usage:
  - api_calls: $0.001 per call (after monthly limit)
  - documents: included in tier
  - premium_templates: $0.50 per usage
  - extra_storage: $0.10/GB/month

IMPLEMENTATION:

1. SUBSCRIPTION CREATION:
   When user upgrades tier:
   - Create Stripe customer
   - Create subscription with tier
   - Store stripe_subscription_id in DB
   - Save billing info

2. USAGE TRACKING:
   Every API call:
   - Increment usage counter
   - Check against quota
   - If exceeded, add metered usage charge
   - Update usage timestamp

3. BILLING CYCLE:
   Monthly:
   - Generate usage summary
   - Create invoice in Stripe
   - Email invoice to customer
   - Update next billing date
   - Check if payment failed

4. WEBHOOK HANDLING:
   Listen for Stripe webhooks:
   - charge.succeeded → log payment
   - charge.failed → notify user, retry
   - customer.subscription.updated → update tier
   - customer.subscription.deleted → downgrade
   - invoice.finalized → email to customer

GENERATE:
1. Stripe service class with:
   - create_subscription()
   - get_subscription()
   - update_subscription()
   - cancel_subscription()
   - create_invoice()
   - refund_charge()

2. Usage tracking:
   - record_api_usage()
   - check_quota()
   - get_usage_stats()

3. Webhook handler:
   POST /api/v1/webhooks/stripe

4. Billing dashboard endpoint:
   GET /api/v1/subscriptions/{org_id}/current
   GET /api/v1/subscriptions/{org_id}/invoices
   GET /api/v1/subscriptions/{org_id}/usage

5. Models:
   - Subscription model
   - Invoice model
   - UsageEvent model

PRICING:
TIER 1 - Free: $0/month
  - 10 projects/month
  - 5 documents/month
  - Basic templates only

TIER 2 - Starter: $29/month
  - 100 projects/month
  - 50 documents/month
  - Custom templates
  - 100 API calls/day
  - Email support

TIER 3 - Pro: $99/month
  - Unlimited projects
  - 500 documents/month
  - All features
  - 10,000 API calls/day
  - Priority support

TIER 4 - Enterprise: Custom pricing
  - Unlimited everything
  - Custom integrations
  - Dedicated support
  - SSO/SAML
  - SLA commitment

TESTING:
- Stripe test keys
- Test webhooks with Stripe CLI
- Example payment flows
```

---

## ✅ PROMPT 7: Monitoring, Logging & Observability

```
I need production-grade monitoring and observability.

IMPLEMENT:

1. ERROR TRACKING (Sentry):
   - Capture all exceptions
   - Release tracking
   - Performance monitoring
   - Alert on error spike (>1% error rate)
   - Source map support
   - Breadcrumb tracking

2. APPLICATION PERFORMANCE MONITORING:
   - Request latency tracking (p50, p95, p99)
   - Database query monitoring
   - Background job monitoring
   - Cost per endpoint tracking
   - Slowest endpoints dashboard

3. STRUCTURED LOGGING:
   - JSON format for easy parsing
   - Correlation ID for request tracing
   - Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
   - Include: timestamp, level, message, context, user_id, org_id
   - Cloudwatch/ELK integration ready

4. METRICS:
   - Real-time dashboard:
     - Active users
     - API calls/minute
     - Document generation time (avg, p95)
     - Error rate
     - Database connection pool usage
     - Redis memory usage
     - Task queue depth

GENERATE:

1. sentry_handler.py:
   - Initialize Sentry with DSN
   - Configure integrations (FastAPI, Celery, SQLAlchemy)
   - Custom error handlers
   - Performance monitoring

2. logging_config.py:
   - Structured JSON logging
   - Log rotation
   - Sentry handler integration
   - Different configs for dev/prod

3. middleware/monitoring.py:
   - Request/response logging
   - Latency tracking
   - Error rate monitoring
   - User identification

4. metrics_provider.py:
   - Prometheus metrics
   - Custom metric collectors
   - Gauge, Counter, Histogram types

5. health_check.py:
   - GET /health → quick health check
   - GET /health/detailed → comprehensive status
   - Database connectivity
   - Redis connectivity
   - Stripe API connectivity
   - External API status

EXAMPLE HEALTH RESPONSE:
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0.0",
    "uptime_seconds": 864000,
    "services": {
        "database": "healthy",
        "redis": "healthy",
        "stripe": "healthy",
        "auth0": "healthy"
    },
    "metrics": {
        "cpu_percent": 45,
        "memory_percent": 62,
        "active_requests": 12,
        "error_rate": "0.02%"
    }
}

DASHBOARD METRICS:
1. Real-time:
   - Requests/sec
   - Error rate
   - P95 latency
   - Active connections

2. Time-series (hourly):
   - Document generation count
   - API calls
   - Error count
   - User signups

3. Alerts:
   - Error rate > 1%
   - P95 latency > 2s
   - Database query > 5s
   - Redis memory > 80%
   - Task queue depth > 1000
   - Disk space < 10%

TOOLS INTEGRATION:
- Sentry for errors
- Prometheus for metrics
- Grafana for dashboards
- Datadog alternative (optional)
- PagerDuty for critical alerts

GENERATE TEST EXAMPLES:
- Trigger intentional error
- Load test metrics
- Alert notification
```

---

## 🎯 QUICK REFERENCE: Which Prompt to Use When

| Goal | Use Prompt |
|------|-----------|
| Setup database for B2B | **Prompt 1** (PostgreSQL Migration) |
| Restructure API | **Prompt 2** (API v1 Redesign) |
| Support enterprise auth | **Prompt 3** (Authentication) |
| Multiple customers safely | **Prompt 4** (Multi-Tenancy) |
| Handle long tasks | **Prompt 5** (Celery + Redis) |
| Get paid & track usage | **Prompt 6** (Stripe Billing) |
| Know what's broken | **Prompt 7** (Monitoring) |

---

## 📌 HOW TO USE IN VS CODE

1. **Open Copilot Chat** (Ctrl+Shift+Alt+Enter or Cmd+Shift+Alt+Enter)
2. **Select the relevant code file** (e.g., app/main.py)
3. **Paste one of the prompts above**
4. **Copilot will generate production-ready code**
5. **Review, test, and iterate**

### Example Workflow:
```
Step 1: Open /backend/alembic/versions/
Step 2: Paste PROMPT 1
Step 3: Copilot generates migration files
Step 4: Review the migrations
Step 5: Run: alembic upgrade head
Step 6: Verify: psql and check tables
Step 7: Move to PROMPT 2
```

---

## ⚙️ ENVIRONMENT SETUP

Before using prompts, ensure your .env has:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/axion_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Stripe
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...

# Auth0
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=...
AUTH0_CLIENT_SECRET=...

# Sentry
SENTRY_DSN=https://...@sentry.io/...

# AWS (for file storage)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
AWS_S3_BUCKET=axion-documents

# LLM
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

```

---

## 📊 SUCCESS METRICS

After implementing each prompt:

| Prompt | Success Metric |
|--------|----------------|
| 1 | Database handles 100K+ requests/day |
| 2 | API response under 200ms |
| 3 | Support 10+ orgs without data leak |
| 4 | 99.9% uptime |
| 5 | Document generation doesn't block UI |
| 6 | $0 payment processing errors |
| 7 | <0.5% error rate, <500ms p95 latency |

Good luck! 🚀
