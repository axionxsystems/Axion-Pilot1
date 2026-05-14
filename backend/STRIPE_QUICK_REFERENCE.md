"""
═══════════════════════════════════════════════════════════════════════════════
STRIPE INTEGRATION - EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════════════════════════
-

PROJECT: Axion-Pilot SaaS Payment Integration
BUILT: May 2026
TIER: Production-Ready

═══════════════════════════════════════════════════════════════════════════════
1. WHAT'S INCLUDED
═══════════════════════════════════════════════════════════════════════════════

✓ STRIPE MODELS (backend/app/models/stripe_billing.py)
  - StripeCustomer: Maps org to Stripe customer
  - StripeSubscription: Subscription records with billing dates
  - UsageMetrics: Monthly usage tracking (resets on cycle)
  - Invoice: Audit trail of all payments
  - PaymentIntent: Track failed/retry payments

✓ STRIPE CONFIGURATION (backend/app/core/stripe_config.py)
  - 5 pricing tiers: Free, Starter, Pro, Teams, Enterprise
  - Exact product/price mapping for Stripe Dashboard
  - Tier limits: projects/month, documents, API calls, team seats
  - Webhook event types
  - Currency support

✓ STRIPE SERVICE (backend/app/services/stripe_service.py)
  - Customer creation & management
  - Checkout session generation
  - Subscription CRUD (create, read, update, cancel)
  - Plan upgrades/downgrades with proration
  - Usage metric tracking
  - Invoice recording

✓ BILLING ROUTES (backend/app/api/v1/billing/routes.py)
  - POST /billing/setup-checkout — Create checkout session
  - GET /billing/subscription/{org_id} — Get subscription details
  - PATCH /billing/subscription/{org_id}/change-plan — Upgrade/downgrade
  - DELETE /billing/subscription/{org_id}/cancel — Cancel subscription
  - GET /billing/usage/{org_id} — Get usage + limits
  - GET /billing/can-generate-project/{org_id} — Check limit

✓ WEBHOOK HANDLER (backend/app/api/v1/billing/webhooks.py)
  - POST /api/v1/billing/webhooks/stripe — Main endpoint
  - Signature verification (security)
  - Idempotent event processing
  - All major Stripe events handled:
    * customer.* events
    * customer.subscription.* events
    * invoice.* events
    * payment_intent.* events

✓ USAGE ENFORCEMENT (backend/app/middleware/usage_enforcement.py)
  - Project limit enforcement (returns 402 if exceeded)
  - API call limit tracking
  - Usage counter increment after successful operations
  - Decorator for easy integration into existing routes

✓ DOCUMENTATION
  - STRIPE_INTEGRATION_GUIDE.py — Comprehensive setup guide
  - This file — Quick reference
  - test_stripe_integration.py — Full test suite with examples

═══════════════════════════════════════════════════════════════════════════════
2. PRICING TIERS AT A GLANCE
═══════════════════════════════════════════════════════════════════════════════

┌─────────────┬──────────┬──────────────────┬──────────────┬───────────────┐
│ Tier        │ Price    │ Projects/Month   │ Team Seats   │ API Calls     │
├─────────────┼──────────┼──────────────────┼──────────────┼───────────────┤
│ Free        │ $0       │ 3                │ 1            │ 1,000         │
│ Starter     │ $29      │ 30               │ 1            │ 10,000        │
│ Pro         │ $99      │ Unlimited        │ 3            │ 100,000       │
│ Teams       │ $299     │ Unlimited        │ Unlimited    │ Unlimited     │
│ Enterprise  │ Custom   │ Unlimited        │ Unlimited    │ Unlimited     │
└─────────────┴──────────┴──────────────────┴──────────────┴───────────────┘

═══════════════════════════════════════════════════════════════════════════════
3. QUICK START (5 STEPS)
═══════════════════════════════════════════════════════════════════════════════

STEP 1: Install Stripe Package
───────────────────────────────
cd backend
pip install stripe  # or already in requirements.txt

STEP 2: Set Environment Variables (.env)
──────────────────────────────────────────
STRIPE_SECRET_KEY=sk_test_YOUR_KEY
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY  
STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_SECRET
CHECKOUT_SUCCESS_URL=http://localhost:3000/billing/success
CHECKOUT_CANCEL_URL=http://localhost:3000/billing/cancel

STEP 3: Create Stripe Products & Prices
────────────────────────────────────────
1. Go to: https://stripe.com/dashboard
2. Products → Create product (Free tier, $0)
3. Products → Create product (Starter tier, $29/month)
4. Repeat for Pro, Teams
5. Copy product IDs to .env

STEP 4: Run Database Migrations
─────────────────────────────────
cd backend
python -m alembic upgrade head
# Creates: stripe_customers, stripe_subscriptions, usage_metrics, etc.

STEP 5: Test with Stripe CLI (Local Development)
──────────────────────────────────────────────────
# Terminal 1: Run backend
python -m uvicorn app.main:app --reload

# Terminal 2: Start Stripe webhook forwarding
stripe listen --forward-to localhost:8000/api/v1/billing/webhooks/stripe

# Terminal 3: Test checkout
curl -X POST http://localhost:8000/api/v1/billing/setup-checkout \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"tier": "starter"}'

═══════════════════════════════════════════════════════════════════════════════
4. KEY FLOWS
═══════════════════════════════════════════════════════════════════════════════

FLOW 1: Free User Hits Limit → Upgrades → Continues
──────────────────────────────────────────────────────
┌─────────────┐
│ Free Tier   │ (3 projects/month)
│ Org Created │
└──────┬──────┘
       │ Generate 3 projects
       ├─ Project 1 ✓
       ├─ Project 2 ✓
       ├─ Project 3 ✓
       ├─ Project 4 ✗ (402 Payment Required)
       │
       └─ User clicks "Upgrade"
           │ POST /setup-checkout
           ├─ Get Stripe checkout URL
           ├─ Redirect to checkout.stripe.com
           ├─ User pays $29/month
           │
           └─ Stripe webhook: subscription.created
               ├─ Create StripeSubscription record
               ├─ Create UsageMetrics (reset to 0)
               ├─ Update Organization.tier = "starter"
               │
               └─ User retries Project 4 ✓
                   (30/month limit, only 3 used so far)


FLOW 2: User Upgrades Plan During Active Subscription
───────────────────────────────────────────────────────
Current: Starter ($29, 30 projects)
Upgrade: Pro ($99, unlimited)

PATCH /change-plan → {"new_tier": "pro"}

Backend:
1. stripe.Subscription.modify(sub_id, 
     items=[{plan: pro_price}],
     proration_behavior="create_prorations"
   )
2. Stripe calculates prorated amount:
   - 20 days left in Starter month = $19 credit
   - 20 days into Pro month = $66 charge
   - User pays: $66 - $19 = $47
3. Update StripeSubscription.tier = "pro"
4. Usage limits immediately increase to unlimited


FLOW 3: Webhook Handles Failed Payment → Retry → Success
────────────────────────────────────────────────────────
Month-end invoice generated:
invoice.payment_succeeded ✓ (Stripe event)
  │ Backend: Create Invoice record, mark paid
  └─ Send receipt email

OR

invoice.payment_failed ✗ (Stripe event)
  │ Backend: Create Invoice record, mark failed
  ├─ Update StripeSubscription.status = "past_due"
  └─ Send "Payment Failed" email with retry link

User fixes payment method in Stripe portal:
invoice.payment_succeeded ✓ (retry event)
  │ Backend: Update Invoice.status = "paid"
  ├─ Update StripeSubscription.status = "active"
  └─ Send "Payment Recovered" email


FLOW 4: Month Ends → Usage Reset
─────────────────────────────────
Current: Projects_generated = 25/30 used

Month ends:
next API call → get_or_create_metrics()
  │ Check: datetime.utcnow() >= reset_date?
  ├─ YES: Reset all counters to 0
  ├─ projects_generated = 0
  ├─ documents_created = 0
  ├─ api_calls = 0
  └─ Set reset_date to new period_end

User can now generate 30 more projects for new month

═══════════════════════════════════════════════════════════════════════════════
5. INTEGRATION WITH EXISTING ENDPOINTS
═══════════════════════════════════════════════════════════════════════════════

TO INTEGRATE USAGE ENFORCEMENT INTO PROJECT GENERATION:

BEFORE (Current Code):
─────────────────────
@router.post("/projects/generate")
async def create_project(request: ProjectRequest, org_id: str, db: Session):
    # ... existing logic ...
    project = await generate_project_logic(request, org_id, db)
    return {"project": project}


AFTER (With Usage Enforcement):
──────────────────────────────
@router.post("/projects/generate")
async def create_project(request: ProjectRequest, org_id: str, db: Session):
    # ← ADD THESE 2 LINES:
    from app.middleware.usage_enforcement import enforce_project_limit, increment_project_count
    enforce_project_limit(org_id, db)  # Raises 402 if over limit
    
    # ... existing logic ...
    project = await generate_project_logic(request, org_id, db)
    
    # ← ADD THIS LINE:
    increment_project_count(org_id, db)  # Increment after success
    
    return {"project": project}

Result:
- If org is free tier and has 3 projects: Returns 402 Payment Required
- If org is pro tier: Always allowed (unlimited)
- Counter increments after successful generation

═══════════════════════════════════════════════════════════════════════════════
6. TESTING WITH STRIPE CLI
═══════════════════════════════════════════════════════════════════════════════

LOCAL WEBHOOK TESTING:

Terminal 1: Start Backend
─────────────────────────
cd backend
python -m uvicorn app.main:app --reload
# Running at http://localhost:8000

Terminal 2: Forward Stripe Webhooks
────────────────────────────────────
stripe listen --forward-to localhost:8000/api/v1/billing/webhooks/stripe

Output:
> Ready! Your webhook signing secret is: whsec_test_1234567890...

Copy this → STRIPE_WEBHOOK_SECRET in .env


Terminal 3: Trigger Test Events
────────────────────────────────
# Test customer created
stripe trigger customer.created

# Test subscription created
stripe trigger customer.subscription.created

# Test payment succeeded
stripe trigger invoice.payment_succeeded

Watch Terminal 1 logs:
> Received Stripe webhook: customer.created
> Created customer xyz for org abc
> Successfully saved customer

Check Database:
SELECT * FROM stripe_customers;  ← Should have new record


═══════════════════════════════════════════════════════════════════════════════
7. PRODUCTION DEPLOYMENT CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

□ Environment
  □ STRIPE_SECRET_KEY=sk_live_... (LIVE key, not test)
  □ All URLs are HTTPS
  □ No hardcoded secrets in code
  □ Secrets in environment or secrets manager

□ Database
  □ Run migrations: alembic upgrade head
  □ All stripe_billing tables created
  □ Indexes on stripe_subscription_id, org_id
  □ Backups automated

□ Stripe Configuration
  □ Add webhook endpoint: https://yourdomain.com/api/v1/billing/webhooks/stripe
  □ Subscribe to all required events
  □ Test webhook delivery (Stripe Dashboard)
  □ Set up Stripe Dashboard alerts

□ Monitoring
  □ Log all webhook events
  □ Alert on failed payments
  □ Monitor webhook delivery latency
  □ Track error rates

□ Security
  □ HTTPS enforced
  □ Webhook signature verification active
  □ Rate limiting on payment endpoints
  □ CORS configured correctly

□ Documentation
  □ Customer billing docs written
  □ Support runbooks created
  □ API documentation updated

═══════════════════════════════════════════════════════════════════════════════
8. COMMON OPERATIONS
═══════════════════════════════════════════════════════════════════════════════

CHECK USER'S CURRENT SUBSCRIPTION:
──────────────────────────────────
GET /api/v1/billing/subscription/org_uuid

Response:
{
  "tier": "pro",
  "status": "active",
  "current_period_start": "2024-09-01",
  "current_period_end": "2024-10-01",
  "cancel_at_period_end": false
}


CHECK CURRENT USAGE:
───────────────────
GET /api/v1/billing/usage/org_uuid

Response:
{
  "tier": "pro",
  "usage": {
    "projects_generated": 15,
    "api_calls": 2400
  },
  "limits": {
    "max_projects_per_month": 999999,
    "max_api_calls": 100000
  }
}


UPGRADE USER FROM STARTER TO PRO:
─────────────────────────────────
PATCH /api/v1/billing/subscription/org_uuid/change-plan
{"new_tier": "pro"}

(Proration calculated automatically by Stripe)


CANCEL USER'S SUBSCRIPTION:
───────────────────────────
DELETE /api/v1/billing/subscription/org_uuid/cancel
{"immediate": false}  # false = cancel at period end, true = immediate


CHECK RECENT INVOICES:
──────────────────────
SELECT * FROM stripe_invoices 
WHERE org_id = 'org_uuid'
ORDER BY created_at DESC
LIMIT 10;


DEBUG: USER CAN'T GENERATE PROJECT
──────────────────────────────────
1. Check subscription:
   GET /api/v1/billing/subscription/org_uuid

2. Check usage:
   GET /api/v1/billing/usage/org_uuid

3. If free tier and 3 projects used:
   - User needs to upgrade
   - Provide checkout link

4. If pro tier and still getting 402:
   - Check UsageMetrics.reset_date
   - May need manual reset if subscription changed mid-cycle
   - UPDATE usage_metrics SET projects_generated = 0 WHERE org_id = 'org_uuid';

═══════════════════════════════════════════════════════════════════════════════
9. ERROR HANDLING
═══════════════════════════════════════════════════════════════════════════════

402 PAYMENT REQUIRED — Usage Limit Exceeded
─────────────────────────────────────────────
{
  "error": "usage_limit_exceeded",
  "message": "Tier 'free' allows 3 projects/month. Current: 3.",
  "tier": "free",
  "limit": 3,
  "current": 3
}

Solution: Upgrade plan via POST /setup-checkout


400 BAD REQUEST — Invalid Tier
───────────────────────────────
{
  "detail": "Invalid tier: invalid_name"
}

Solution: Use valid tier: free, starter, pro, teams, enterprise


404 NOT FOUND — No Active Subscription
────────────────────────────────────────
GET /subscription/org_uuid returns default free tier info

Solution: Normal — free tier users have no subscription


401 UNAUTHORIZED — Missing JWT Token
──────────────────────────────────────
{
  "detail": "Not authenticated"
}

Solution: Include Authorization header with valid JWT token


500 INTERNAL SERVER ERROR — Stripe API Error
──────────────────────────────────────────────
Check backend logs for detailed error:
log: "Stripe API error: ..."

Solution:
- Verify Stripe API key correct
- Check Stripe status page
- Retry operation

═══════════════════════════════════════════════════════════════════════════════
10. FILES CREATED / MODIFIED
═══════════════════════════════════════════════════════════════════════════════

NEW FILES:
──────────
✓ backend/app/models/stripe_billing.py
  - 7 models: StripeCustomer, StripeSubscription, UsageMetrics, Invoice, PaymentIntent

✓ backend/app/core/stripe_config.py
  - Configuration, tier definitions, constants

✓ backend/app/services/stripe_service.py
  - StripeCustomerService, StripeSubscriptionService, UsageMetricsService, StripeInvoiceService

✓ backend/app/api/v1/billing/routes.py
  - 6 endpoints for checkout, subscriptions, usage

✓ backend/app/api/v1/billing/webhooks.py
  - Webhook handler with signature verification

✓ backend/app/middleware/usage_enforcement.py
  - Usage limit checks, decorators

✓ backend/STRIPE_INTEGRATION_GUIDE.py
  - Comprehensive setup guide (12 sections)

✓ backend/tests/test_stripe_integration.py
  - Full test suite with examples

MODIFIED FILES:
────────────────
✓ backend/app/main.py
  - Added stripe_billing model import

✓ backend/app/api/v1/__init__.py
  - Added billing router

✓ backend/requirements.txt
  - Added stripe package

✓ backend/.env
  - Added Stripe configuration section

═══════════════════════════════════════════════════════════════════════════════
11. NEXT STEPS
═══════════════════════════════════════════════════════════════════════════════

1. GET STRIPE API KEYS
   └─ Create Stripe account: https://stripe.com
   └─ Developers → API Keys → Copy test keys
   └─ Save to .env

2. CREATE STRIPE PRODUCTS
   └─ Dashboard → Products → Create 5 products (Free, Starter, Pro, Teams, Enterprise)
   └─ Add pricing tiers ($0, $29, $99, $299, custom)
   └─ Copy product IDs to .env

3. INTEGRATE WITH PROJECT GENERATION
   └─ Add enforce_project_limit() call before generation
   └─ Add increment_project_count() after success
   └─ Test with different tiers

4. TEST WITH STRIPE CLI
   └─ Install Stripe CLI
   └─ Run: stripe listen --forward-to localhost:8000/api/v1/billing/webhooks/stripe
   └─ Test events: stripe trigger customer.subscription.created

5. DEPLOY TO PRODUCTION
   └─ Use sk_live_* keys
   └─ Update webhook URL to production domain (HTTPS)
   └─ Run database migrations
   └─ Monitor webhook delivery

6. FRONTEND INTEGRATION
   └─ Add checkout button (redirects to setup-checkout)
   └─ Add billing dashboard (display subscription, usage)
   └─ Handle 402 errors gracefully (show upgrade prompt)

═══════════════════════════════════════════════════════════════════════════════
12. SUPPORT / FAQ
═══════════════════════════════════════════════════════════════════════════════

Q: Where do I get Stripe API keys?
A: https://dashboard.stripe.com/apikeys (test keys start with sk_test_)

Q: Can I test without real credit card?
A: Yes! Use Stripe test card: 4242 4242 4242 4242 with any future expiry/CVC

Q: How do I test webhooks locally?
A: Use Stripe CLI: stripe listen --forward-to localhost:8000/...

Q: What if a webhook fails?
A: Stripe retries automatically. All handlers are idempotent (safe to retry).

Q: How do I handle refunds?
A: Through Stripe Dashboard (Issues refund, triggers webhook, backend records it)

Q: Can I change pricing mid-month?
A: Yes, with proration. Stripe automatically credits/charges difference.

Q: What happens when user's card fails?
A: Invoice marked as past_due, user gets email, can retry in Stripe portal.

═══════════════════════════════════════════════════════════════════════════════

For comprehensive details, see: STRIPE_INTEGRATION_GUIDE.py
For tests and examples, see: tests/test_stripe_integration.py
For direct implementation, check individual files in backend/app/

═══════════════════════════════════════════════════════════════════════════════
"""

print(__doc__)
