"""
STRIPE INTEGRATION - COMPLETE SETUP & EXAMPLE WORKFLOW
=============================================================================

This document provides the complete Stripe integration for Axion-Pilot.
Covers setup, configuration, API usage, webhook handling, and testing.

KEY COMPONENTS:
1. Database Models (stripe_billing.py)
2. Configuration & Constants (stripe_config.py)
3. Stripe Service (stripe_service.py)
4. Billing Routes (api/v1/billing/routes.py)
5. Webhook Handler (api/v1/billing/webhooks.py)
6. Usage Enforcement (middleware/usage_enforcement.py)
"""

# =============================================================================
# SECTION 1: STRIPE ACCOUNT SETUP
# =============================================================================

"""
STEP 1.1: Create Stripe Account
- Go to: https://stripe.com
- Create account (test mode is default)
- Verify email

STEP 1.2: Get API Keys
- Dashboard → Developers → API Keys
- Copy:
  * Secret Key (sk_test_...)      → STRIPE_SECRET_KEY
  * Publishable Key (pk_test_...) → STRIPE_PUBLISHABLE_KEY
- Save to .env file

STEP 1.3: Setup Webhook Secret
- Dashboard → Developers → Webhooks
- Add endpoint: https://yourdomain.com/api/v1/billing/webhooks/stripe
- Copy Signing secret (whsec_test_...) → STRIPE_WEBHOOK_SECRET
- Subscribe to these events:
  * customer.created
  * customer.updated
  * customer.deleted
  * customer.subscription.created
  * customer.subscription.updated
  * customer.subscription.deleted
  * invoice.created
  * invoice.payment_succeeded
  * invoice.payment_failed
  * invoice.paid
  * payment_intent.succeeded
  * payment_intent.payment_failed

STEP 1.4: Create Products & Prices in Stripe Dashboard
  (See SECTION 2 for exact setup instructions)
"""

# =============================================================================
# SECTION 2: STRIPE PRODUCT SETUP (Exact Configuration)
# =============================================================================

"""
Log in to Stripe Dashboard → Products

PRODUCT 1: FREE TIER
├─ Name: AxionPilot Free
├─ Type: Service
├─ Price:
│  ├─ Billing period: Monthly
│  ├─ Amount: $0 USD
│  └─ Price ID: price_free_1234567890
└─ Limits:
   ├─ 3 projects/month
   ├─ 5 documents
   └─ 1,000 API calls

PRODUCT 2: STARTER TIER
├─ Name: AxionPilot Starter
├─ Type: Service
├─ Price:
│  ├─ Billing period: Monthly
│  ├─ Amount: $29 USD
│  ├─ Trial period: 14 days (optional)
│  └─ Price ID: price_starter_1234567890
└─ Limits:
   ├─ 30 projects/month
   ├─ 50 documents
   └─ 10,000 API calls

PRODUCT 3: PRO TIER
├─ Name: AxionPilot Pro
├─ Type: Service
├─ Price:
│  ├─ Billing period: Monthly
│  ├─ Amount: $99 USD
│  ├─ Trial period: 14 days (optional)
│  └─ Price ID: price_pro_1234567890
└─ Limits:
   ├─ Unlimited projects
   ├─ Unlimited documents
   ├─ 100,000 API calls
   └─ 3 team seats

PRODUCT 4: TEAMS TIER
├─ Name: AxionPilot Teams
├─ Type: Service
├─ Price:
│  ├─ Billing period: Monthly
│  ├─ Amount: $299 USD
│  ├─ Trial period: 14 days (optional)
│  └─ Price ID: price_teams_1234567890
└─ Limits:
   ├─ Unlimited projects
   ├─ Unlimited documents
   ├─ Unlimited API calls
   └─ Unlimited team seats

PRODUCT 5: ENTERPRISE
└─ No fixed price in Stripe (custom pricing)
   Contact sales: sales@axionpilot.com

UPDATE .env with product IDs:
STRIPE_PRODUCT_FREE=prod_free_1234567890
STRIPE_PRODUCT_STARTER=prod_starter_1234567890
STRIPE_PRICE_STARTER=price_starter_1234567890
STRIPE_PRODUCT_PRO=prod_pro_1234567890
STRIPE_PRICE_PRO=price_pro_1234567890
STRIPE_PRODUCT_TEAMS=prod_teams_1234567890
STRIPE_PRICE_TEAMS=price_teams_1234567890
"""

# =============================================================================
# SECTION 3: ENVIRONMENT SETUP
# =============================================================================

"""
.env Configuration:

# Stripe API Keys (from Dashboard)
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLIC_KEY
STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_WEBHOOK_SECRET

# Stripe Environment
STRIPE_ENV=test  # use 'live' in production

# Product IDs (from Dashboard → Products)
STRIPE_PRODUCT_FREE=prod_abc123xyz
STRIPE_PRODUCT_STARTER=prod_def456uvw
STRIPE_PRICE_STARTER=price_starter_1234567890
# ... etc for other tiers

# Checkout Redirect URLs (where to send user after payment)
CHECKOUT_SUCCESS_URL=https://yourdomain.com/billing/success
CHECKOUT_CANCEL_URL=https://yourdomain.com/billing/cancel
"""

# =============================================================================
# SECTION 4: COMPLETE WORKFLOW EXAMPLE
# =============================================================================

"""
WORKFLOW: Free User → Creates Org → Hits Project Limit → Upgrades → Success

STEP 1: Organization Created (Free Tier by Default)
────────────────────────────────────────────────────
POST /api/organizations
{
  "name": "Acme Corp",
  "slug": "acme-corp"
}

Response:
{
  "id": "org_uuid_1234",
  "name": "Acme Corp",
  "tier": "free"  ← Free tier assigned
}

Database Records Created:
- Organization(id=org_uuid_1234, tier="free")
- UsageMetrics(org_id=org_uuid_1234, projects_generated=0, limit=3)


STEP 2: User Generates 3 Projects (At Free Tier Limit)
───────────────────────────────────────────────────────
POST /api/projects/generate
{
  "title": "Chat App",
  "description": "Real-time chat application"
}

Backend:
1. Check limit: enforce_project_limit(org_id, db)
   - Query subscription or default to free tier
   - Check: metrics.projects_generated (3) < limit (3) ? NO → Reject
   
2. If allowed, generate project...
   
3. Increment counter: increment_project_count(org_id, db)

After 3 projects:
UsageMetrics.projects_generated = 3


STEP 3: User Tries 4th Project → Hits Limit
────────────────────────────────────────────
POST /api/projects/generate
{
  "title": "Task Manager",
  "description": "Team task management"
}

Backend Check:
enforce_project_limit(org_id="org_uuid_1234", db)
  → check_project_limit("org_uuid_1234")
    → subscription = None (free tier)
    → tier = "free"
    → limits = {"max_projects_per_month": 3, ...}
    → metrics.projects_generated = 3
    → 3 >= 3 ? YES → LIMIT EXCEEDED

Response: 402 Payment Required
{
  "error": "usage_limit_exceeded",
  "message": "Tier 'free' allows 3 projects/month. Current: 3.",
  "tier": "free",
  "limit": 3,
  "current": 3
}

Frontend displays: "Upgrade to create more projects"


STEP 4: User Starts Checkout for Starter Tier
──────────────────────────────────────────────
POST /api/v1/billing/setup-checkout
{
  "tier": "starter",
  "quantity": 1
}

Backend:
1. Create Stripe Customer (if not exists):
   stripe.Customer.create(
     email="user@acme.com",
     metadata={"org_id": "org_uuid_1234"}
   )
   → Returns: cus_stripe_id_1234
   → Saved: StripeCustomer(org_id, stripe_customer_id, ...)

2. Create Checkout Session:
   stripe.checkout.Session.create(
     customer="cus_stripe_id_1234",
     line_items=[{"price": "price_starter_1234567890", "quantity": 1}],
     mode="subscription",
     success_url="https://yourdomain.com/billing/success?session_id={CHECKOUT_SESSION_ID}",
     cancel_url="https://yourdomain.com/billing/cancel",
     trial_end=1234567890  # 14 days from now
   )
   → Returns: https://checkout.stripe.com/pay/cs_1234567890...

Response:
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_1234567890...",
  "session_id": "cs_1234567890..."
}

Frontend: Redirect to checkout_url


STEP 5: User Completes Payment on Stripe
────────────────────────────────────────
User enters:
- Credit card: 4242 4242 4242 4242 (Stripe test card)
- Expiry: 12/25
- CVC: 123

Stripe processes payment → Creates subscription


STEP 6: Webhook: customer.subscription.created
───────────────────────────────────────────────
Stripe sends: POST /api/v1/billing/webhooks/stripe
Event Type: customer.subscription.created
Event Data:
{
  "id": "sub_stripe_id_1234567890",
  "customer": "cus_stripe_id_1234",
  "items": {
    "data": [
      {
        "plan": {
          "id": "price_starter_1234567890",
          "product": "prod_starter_1234567890"
        }
      }
    ]
  },
  "status": "trialing",
  "current_period_start": 1695000000,
  "current_period_end": 1697678400,  # 30 days later
  "trial_start": 1695000000,
  "trial_end": 1695000000 + (14 * 86400),  # 14 days later
  "metadata": {"org_id": "org_uuid_1234", "tier": "starter"},
  ...
}

Backend Processing:
1. Verify signature: stripe.Webhook.construct_event(...)
2. Extract event_type = "customer.subscription.created"
3. Call handle_subscription_created(db, event_data)
4. StripeSubscriptionService.save_subscription(db, org_id, event_data)
   → Create StripeSubscription record:
     StripeSubscription(
       org_id="org_uuid_1234",
       stripe_subscription_id="sub_stripe_id_1234567890",
       stripe_product_id="prod_starter_1234567890",
       stripe_price_id="price_starter_1234567890",
       tier="starter",
       status="trialing",
       current_period_start=datetime(...),
       current_period_end=datetime(...),
       trial_start=datetime(...),
       trial_end=datetime(...)
     )
   → Create UsageMetrics record:
     UsageMetrics(
       org_id="org_uuid_1234",
       projects_generated=0,  ← Reset!
       documents_created=0,
       api_calls=0,
       billing_period_start=...,
       billing_period_end=...,
       reset_date=...
     )

Database After Webhook:
- StripeCustomer(org_id, stripe_customer_id=cus_stripe_id_1234)
- StripeSubscription(org_id, tier="starter", status="trialing")
- UsageMetrics(org_id, projects_generated=0, limit=30)  ← New limit!


STEP 7: User Retries 4th Project → Now Allowed
──────────────────────────────────────────────
POST /api/projects/generate
{
  "title": "Task Manager",
  "description": "Team task management"
}

Backend:
1. enforce_project_limit(org_id="org_uuid_1234", db)
   → subscription = StripeSubscription(..., tier="starter")
   → limits = {"max_projects_per_month": 30}
   → metrics.projects_generated = 0
   → 0 < 30 ? YES → Allowed!

2. Generate project...

3. increment_project_count(org_id, db)
   → metrics.projects_generated = 1

Response: 200 OK - Project generated!


STEP 8: Query Usage Stats
─────────────────────────
GET /api/v1/billing/usage/org_uuid_1234

Response:
{
  "tier": "starter",
  "usage": {
    "projects_generated": 1,
    "documents_created": 0,
    "api_calls": 0
  },
  "limits": {
    "max_projects_per_month": 30,
    "max_documents": 50,
    "max_api_calls": 10000,
    "max_team_seats": 1
  },
  "billing_period": {
    "start": "2024-09-01T00:00:00",
    "end": "2024-10-01T00:00:00",
    "remaining_days": 27
  }
}


STEP 9: User Upgrades to Pro (During Active Subscription)
─────────────────────────────────────────────────────────
PATCH /api/v1/billing/subscription/org_uuid_1234/change-plan
{
  "new_tier": "pro"
}

Backend:
1. Get active subscription (starter)
2. stripe.Subscription.modify(sub_stripe_id_1234567890,
     items=[{plan: "price_pro_1234567890"}],
     proration_behavior="create_prorations"
   )
3. Save updated subscription in DB

Stripe creates prorated invoice:
- Refund for unused days of Starter ($29 - 25 days = ~$21)
- Charge for Pro ($99 - 25 days = ~$78)
- Net: User pays ~$57 for upgrade

Database Updated:
StripeSubscription(org_id, tier="pro", status="active", ...)


STEP 10: First Billing Cycle Completes → Webhook: invoice.payment_succeeded
───────────────────────────────────────────────────────────────────────────
14 days later (after trial ends):

Stripe sends: POST /api/v1/billing/webhooks/stripe
Event: invoice.payment_succeeded
{
  "id": "in_stripe_id_1234567890",
  "customer": "cus_stripe_id_1234",
  "subscription": "sub_stripe_id_1234567890",
  "amount_paid": 9900,  # $99 in cents
  "status": "paid",
  "paid_at": 1695604800,  ← Timestamp
  ...
}

Backend:
1. StripeInvoiceService.save_invoice(db, event_data)
   → Create Invoice record:
     Invoice(
       org_id="org_uuid_1234",
       stripe_invoice_id="in_stripe_id_1234567890",
       amount=9900,
       status="paid",
       paid_at=datetime(...)
     )

2. TODO: Send receipt email, update accounting, etc.


STEP 11: User Cancels Subscription (At End of Period)
──────────────────────────────────────────────────────
DELETE /api/v1/billing/subscription/org_uuid_1234/cancel
{
  "immediate": false  ← Cancel at end of period
}

Backend:
1. stripe.Subscription.modify(sub_stripe_id_1234567890,
     cancel_at_period_end=true
   )
2. Update DB: StripeSubscription.cancel_at_period_end = true

Result: User keeps access until 2024-10-01, then reverts to free tier


STEP 12: Billing Cycle Ends → Usage Reset
──────────────────────────────────────────
2024-10-01 00:00:00:

On next API call:
1. get_or_create_metrics(db, org_id)
2. if datetime.utcnow() >= metrics.reset_date:
   → Reset metrics.projects_generated = 0
   → Reset metrics.documents_created = 0
   → Reset metrics.api_calls = 0
   → Update reset_date for next month

Usage counter starts fresh for new month!
"""

# =============================================================================
# SECTION 5: API USAGE EXAMPLES (cURL / Python)
# =============================================================================

"""
EXAMPLE 1: Create Checkout Session
────────────────────────────────────
curl -X POST http://localhost:8000/api/v1/billing/setup-checkout \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "tier": "starter",
    "quantity": 1
  }'

Response:
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_...",
  "session_id": "cs_..."
}


EXAMPLE 2: Get Active Subscription
──────────────────────────────────
curl -X GET http://localhost:8000/api/v1/billing/subscription/org_uuid_1234 \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

Response:
{
  "tier": "pro",
  "status": "active",
  "current_period_start": "2024-09-01T00:00:00",
  "current_period_end": "2024-10-01T00:00:00",
  "cancel_at_period_end": false,
  "stripe_subscription_id": "sub_..."
}


EXAMPLE 3: Change Plan
──────────────────────
curl -X PATCH http://localhost:8000/api/v1/billing/subscription/org_uuid_1234/change-plan \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"new_tier": "teams"}'

Response:
{
  "message": "Plan changed to teams",
  "tier": "teams",
  "status": "active"
}


EXAMPLE 4: Get Usage & Limits
──────────────────────────────
curl -X GET http://localhost:8000/api/v1/billing/usage/org_uuid_1234 \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

Response:
{
  "tier": "pro",
  "usage": {
    "projects_generated": 15,
    "documents_created": 42,
    "api_calls": 2500
  },
  "limits": {
    "max_projects_per_month": 999999,
    "max_documents": 999999,
    "max_api_calls": 100000,
    "max_team_seats": 3
  },
  "billing_period": {
    "start": "2024-09-01T00:00:00",
    "end": "2024-10-01T00:00:00",
    "remaining_days": 18
  }
}


EXAMPLE 5: Check if Can Generate Project
─────────────────────────────────────────
curl -X GET http://localhost:8000/api/v1/billing/can-generate-project/org_uuid_1234 \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

Response (Allowed):
{
  "can_generate": true,
  "remaining": 19,
  "tier": "pro"
}

Response (Denied):
{
  "can_generate": false,
  "reason": "Tier free limit (3 projects/month) reached",
  "tier": "free",
  "remaining": 0
}


EXAMPLE 6: Cancel Subscription
───────────────────────────────
curl -X DELETE http://localhost:8000/api/v1/billing/subscription/org_uuid_1234/cancel \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d '{"immediate": false}'

Response:
{
  "message": "Subscription cancelled",
  "tier": "pro",
  "status": "active",
  "cancel_at_period_end": true,
  "canceled_at": null  ← Will be set at period end
}
"""

# =============================================================================
# SECTION 6: PROJECT GENERATION WITH USAGE ENFORCEMENT
# =============================================================================

"""
INTEGRATING USAGE CHECKS INTO PROJECT GENERATION:

Current project generation endpoint (backend/app/api/projects.py):

@router.post("/generate")
async def generate_project(
    request: ProjectGenerationRequest,
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    # ADD THIS:
    from app.middleware.usage_enforcement import enforce_project_limit, increment_project_count
    
    # Check usage limit BEFORE generation
    enforce_project_limit(org_id, db)  # Raises 402 if over limit
    
    # ... existing project generation logic ...
    
    # Increment counter AFTER successful generation
    increment_project_count(org_id, db)
    
    return project_response


EXAMPLE: Endpoint with Enforcement
───────────────────────────────────
@router.post("/api/projects/generate")
async def create_project(
    request: ProjectGenerationRequest,
    org_id: str = Depends(get_current_org_id),
    db: Session = Depends(get_db),
):
    \"\"\"Generate new project with usage limit enforcement.\"\"\"
    
    # 1. Check if user can generate
    from app.middleware.usage_enforcement import enforce_project_limit
    enforce_project_limit(org_id, db)  # Raises HTTPException(402) if denied
    
    # 2. Generate project
    project = await generate_project_logic(request, org_id, db)
    
    # 3. Increment counter
    from app.middleware.usage_enforcement import increment_project_count
    increment_project_count(org_id, db)
    
    return {"project": project}
"""

# =============================================================================
# SECTION 7: WEBHOOK TESTING WITH STRIPE CLI
# =============================================================================

"""
LOCAL WEBHOOK TESTING:

Step 1: Download Stripe CLI
- macOS: brew install stripe/stripe-cli/stripe
- Windows: https://github.com/stripe/stripe-cli/releases
- Linux: https://stripe.com/docs/stripe-cli/install

Step 2: Login to Stripe
stripe login
# Opens browser, click "Allow access"

Step 3: Forward Webhooks to Local Server
stripe listen --forward-to localhost:8000/api/v1/billing/webhooks/stripe

Output:
> Ready! Your webhook signing secret is: whsec_test_1234567890...

Copy this signing secret → STRIPE_WEBHOOK_SECRET in .env

Step 4: Trigger Test Events (in another terminal)
stripe trigger customer.subscription.created

Output:
> Forwarding event to http://localhost:8000/api/v1/billing/webhooks/stripe...

Step 5: Check Backend Logs
Backend should log:
"Received Stripe webhook: customer.subscription.created"

Step 6: Verify Database
Check stripe_subscriptions table, should have new record.

AVAILABLE TEST EVENTS:
stripe trigger customer.created
stripe trigger customer.updated
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted
stripe trigger invoice.created
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
stripe trigger payment_intent.succeeded
stripe trigger payment_intent.payment_failed
"""

# =============================================================================
# SECTION 8: SECURITY BEST PRACTICES
# =============================================================================

"""
✓ WEBHOOK SIGNATURE VERIFICATION
  - ALWAYS validate stripe-signature header
  - Use stripe.Webhook.construct_event() to verify
  - Implemented in: app/api/v1/billing/webhooks.py

✓ API KEY MANAGEMENT
  - Never commit STRIPE_SECRET_KEY to git
  - Store in .env file (in .gitignore)
  - Use different keys for test vs. live mode
  - Rotate keys regularly in Stripe Dashboard

✓ IDEMPOTENT OPERATIONS
  - All webhook handlers are idempotent
  - Use database constraints (UNIQUE stripe_subscription_id, etc.)
  - Safe to retry failed webhooks
  - Prevents duplicate charges

✓ RATE LIMITING
  - Project generation already has rate limiting
  - Usage limits prevent abuse
  - Free tier capped at 3 projects/month

✓ HTTPS ONLY
  - Webhook URL must be HTTPS in production
  - Never send payment data over HTTP
  - Use SSL certificates

✓ ERROR HANDLING
  - Never expose full error messages to users
  - Log errors server-side for debugging
  - Return generic error to frontend
  - Handle gracefully: connection timeouts, API errors

✓ PCI COMPLIANCE
  - Never handle raw card data
  - Stripe handles all PCI compliance
  - Use Stripe Checkout (not custom forms)
  - Validate webhook signatures

✓ 3D SECURE / SCA
  - Stripe automatically handles Strong Customer Authentication
  - User may need to verify payment with bank
  - Handled transparently in Stripe Checkout
"""

# =============================================================================
# SECTION 9: TROUBLESHOOTING
# =============================================================================

"""
ISSUE 1: "STRIPE_SECRET_KEY not set or invalid"
SOLUTION:
- Check .env file has STRIPE_SECRET_KEY=sk_test_...
- Make sure it starts with sk_test_ (test) or sk_live_ (production)
- Reload environment: export $(cat .env | xargs)

ISSUE 2: Webhook not received
SOLUTION:
- Check webhook URL in Stripe Dashboard (must be HTTPS in prod)
- Use stripe CLI locally: stripe listen --forward-to localhost:8000/...
- Check backend logs for 200 response
- Verify webhook signing secret in .env

ISSUE 3: "Signature verification failed"
SOLUTION:
- STRIPE_WEBHOOK_SECRET must match signing secret in Stripe Dashboard
- Must use correct secret for test/live mode
- Check no trailing spaces in .env

ISSUE 4: Checkout URL returns 400
SOLUTION:
- Check CHECKOUT_SUCCESS_URL and CHECKOUT_CANCEL_URL in .env
- Must be valid URLs (http://... or https://...)
- In development, can use http://localhost:3000/...

ISSUE 5: Customer not found in webhook
SOLUTION:
- Check StripeCustomer record was created before webhook
- May need to query Stripe API directly:
  stripe customers retrieve cus_...

ISSUE 6: Usage limit always rejected
SOLUTION:
- Check UsageMetrics record exists for org
- Query database: SELECT * FROM usage_metrics WHERE org_id = '...'
- Verify billing_period dates are correct

ISSUE 7: Billing date not resetting
SOLUTION:
- Check current_period_end matches reset_date
- May need to manually update after subscription change
- Reset happens on next API call after reset_date
"""

# =============================================================================
# SECTION 10: MONITORING & OPERATIONS
# =============================================================================

"""
KEY METRICS TO MONITOR:

1. Subscription Health
   - SELECT COUNT(*) FROM stripe_subscriptions WHERE status = 'active'
   - SELECT COUNT(*) FROM stripe_subscriptions WHERE status = 'past_due'
   - Alert if past_due count increases

2. Payment Success Rate
   - SELECT COUNT(*) FROM stripe_invoices WHERE status = 'paid'
   - SELECT COUNT(*) FROM stripe_invoices WHERE status = 'failed'
   - Target: >99% success rate

3. Usage Patterns
   - SELECT AVG(projects_generated) FROM usage_metrics WHERE tier = 'pro'
   - SELECT MAX(api_calls) FROM usage_metrics
   - Identify power users for retention focus

4. Revenue
   - SELECT SUM(amount) FROM stripe_invoices 
     WHERE status = 'paid' AND DATE(paid_at) >= DATE_SUB(NOW(), INTERVAL 30 DAY)
   - MRR (Monthly Recurring Revenue)

5. Churn Rate
   - SELECT COUNT(*) FROM stripe_subscriptions 
     WHERE status = 'canceled' AND canceled_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)

AUTOMATED ALERTS:
- Monitor /health endpoint for webhook failures
- Set up Stripe Dashboard alerts for:
  * Multiple failed payment attempts
  * Subscription cancellations
  * Webhook delivery failures
"""

# =============================================================================
# SECTION 11: TESTING CHECKLIST
# =============================================================================

"""
MANUAL TESTING CHECKLIST:

□ 1. Free Tier Workflow
   □ Create org (default free tier)
   □ Generate 3 projects (all succeed)
   □ Try 4th project (403 Payment Required)
   
□ 2. Checkout Flow
   □ Call POST /setup-checkout with tier=starter
   □ Get checkout_url
   □ Open URL in browser
   □ Use test card: 4242 4242 4242 4242
   □ Complete payment
   □ Check webhook received (stripe logs)
   
□ 3. Subscription Created
   □ Verify StripeCustomer record created
   □ Verify StripeSubscription record created
   □ Verify UsageMetrics reset to 0
   □ Verify org tier updated
   
□ 4. Usage Tracking
   □ Generate projects, check counter increments
   □ GET /usage, verify correct counts
   □ GET /can-generate-project, check remaining
   
□ 5. Plan Upgrade
   □ PATCH /change-plan from starter to pro
   □ Verify Stripe subscription updated
   □ Verify DB record updated
   □ Generate 50+ projects (should work, pro has 999999 limit)
   
□ 6. Cancellation
   □ DELETE /cancel with immediate=false
   □ Verify cancel_at_period_end=true
   □ Simulate period end (manually reset reset_date)
   □ Try generate project (should fail, free tier limit)
   
□ 7. Webhook Signatures
   □ Use stripe CLI: stripe listen --forward-to ...
   □ Trigger events: stripe trigger customer.subscription.created
   □ Verify backend logs show received
   □ Verify database updated

□ 8. Error Handling
   □ Invalid tier: POST /setup-checkout with tier=invalid
   □ Wrong org_id: GET /subscription/wrong_id (403)
   □ No subscription: GET /subscription/new_org (should return free tier info)
   □ Missing JWT token: GET /usage (401)

LOAD TESTING:
   □ Simulate 100 concurrent checkouts
   □ Verify no duplicate subscriptions
   □ Check webhook delivery time <5s
"""

# =============================================================================
# SECTION 12: PRODUCTION DEPLOYMENT
# =============================================================================

"""
PRODUCTION CHECKLIST:

□ Database
  □ Run migrations: alembic upgrade head
  □ All stripe_billing tables created
  □ Indexes on stripe_subscription_id, org_id
  □ Backup plan in place

□ Environment Variables
  □ STRIPE_SECRET_KEY=sk_live_... (LIVE key)
  □ STRIPE_PUBLISHABLE_KEY=pk_live_...
  □ STRIPE_WEBHOOK_SECRET=whsec_live_...
  □ STRIPE_ENV=live
  □ CHECKOUT_SUCCESS_URL=https://yourdomain.com/...
  □ All URLs use HTTPS

□ Stripe Configuration
  □ Add webhook endpoint: https://yourdomain.com/api/v1/billing/webhooks/stripe
  □ Enable all required events
  □ Test webhook delivery (Dashboard → Webhooks → Send test)
  □ Set up alerts in Stripe Dashboard

□ Monitoring
  □ Set up logging for all webhook events
  □ Monitor error rates
  □ Set up alerts for failed payments
  □ Monitor API response times

□ Security
  □ HTTPS enforced everywhere
  □ Secrets not in code/git
  □ WAF rules for /webhooks endpoint
  □ Rate limiting active
  □ CORS properly configured

□ Backup & Recovery
  □ Stripe data automatically backed up by Stripe
  □ Local DB backups automated
  □ Disaster recovery plan documented
  □ Test restore procedure

□ Documentation
  □ Customer support docs for billing
  □ Runbooks for common issues
  □ Upgrade/downgrade procedures documented
  □ Cancellation process clear
"""

print(__doc__)
