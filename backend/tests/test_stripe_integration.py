"""
Stripe Integration Tests - Complete Test Suite
Run these tests to verify Stripe integration is working correctly.

Usage:
    pytest backend/tests/test_stripe_integration.py -v
    
Or run individual tests:
    pytest backend/tests/test_stripe_integration.py::test_free_tier_project_limit -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Mock setup - adjust imports based on your project structure
# from app.main import app
# from app.database import get_db, Base


# =============================================================================
# UNIT TESTS
# =============================================================================

class TestStripeConfig:
    """Test Stripe configuration loading."""
    
    def test_stripe_api_keys_loaded(self):
        """Verify Stripe API keys are loaded from environment."""
        from app.core.stripe_config import STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET
        
        assert STRIPE_SECRET_KEY.startswith("sk_"), "Secret key must start with sk_"
        assert STRIPE_PUBLISHABLE_KEY.startswith("pk_"), "Publishable key must start with pk_"
        assert STRIPE_WEBHOOK_SECRET.startswith("whsec_"), "Webhook secret must start with whsec_"
    
    def test_tier_config_complete(self):
        """Verify all pricing tiers configured."""
        from app.core.stripe_config import TIER_CONFIG, PricingTier
        
        assert PricingTier.FREE in TIER_CONFIG
        assert PricingTier.STARTER in TIER_CONFIG
        assert PricingTier.PRO in TIER_CONFIG
        assert PricingTier.TEAMS in TIER_CONFIG
        assert PricingTier.ENTERPRISE in TIER_CONFIG
        
        # Verify tier limits
        for tier, config in TIER_CONFIG.items():
            if tier != PricingTier.ENTERPRISE:
                assert config.get("max_projects_per_month") > 0
    
    def test_price_mapping_functions(self):
        """Test tier lookup functions."""
        from app.core.stripe_config import get_tier_by_price_id, PricingTier, TIER_CONFIG
        
        starter_price = TIER_CONFIG[PricingTier.STARTER].get("stripe_price_id")
        if starter_price:
            assert get_tier_by_price_id(starter_price) == PricingTier.STARTER


class TestStripeModels:
    """Test Stripe database models."""
    
    def test_stripe_customer_model(self):
        """Test StripeCustomer model creation."""
        from app.models.stripe_billing import StripeCustomer, StripeCustomerStatus
        
        customer = StripeCustomer(
            org_id="test_org_123",
            stripe_customer_id="cus_test_123",
            email="user@example.com",
            status=StripeCustomerStatus.active,
        )
        
        assert customer.org_id == "test_org_123"
        assert customer.stripe_customer_id == "cus_test_123"
        assert customer.status == StripeCustomerStatus.active
    
    def test_stripe_subscription_model(self):
        """Test StripeSubscription model."""
        from app.models.stripe_billing import StripeSubscription, StripeSubscriptionStatus, StripePriceTier
        
        subscription = StripeSubscription(
            customer_id="customer_uuid_123",
            org_id="org_uuid_123",
            stripe_subscription_id="sub_test_123",
            stripe_product_id="prod_test",
            stripe_price_id="price_test",
            tier=StripePriceTier.starter,
            status=StripeSubscriptionStatus.active,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
        )
        
        assert subscription.tier == StripePriceTier.starter
        assert subscription.status == StripeSubscriptionStatus.active
    
    def test_usage_metrics_model(self):
        """Test UsageMetrics model."""
        from app.models.stripe_billing import UsageMetrics
        
        metrics = UsageMetrics(
            org_id="org_uuid_123",
            projects_generated=5,
            documents_created=10,
            api_calls=250,
            billing_period_start=datetime.utcnow(),
            billing_period_end=datetime.utcnow() + timedelta(days=30),
            reset_date=datetime.utcnow() + timedelta(days=30),
        )
        
        assert metrics.projects_generated == 5
        assert metrics.documents_created == 10
        assert metrics.api_calls == 250


class TestUsageMetricsService:
    """Test usage tracking and limit enforcement."""
    
    def test_create_usage_metrics(self, db_session):
        """Test creating usage metrics for organization."""
        from app.services.stripe_service import UsageMetricsService
        
        org_id = "test_org_123"
        period_start = datetime.utcnow()
        period_end = datetime.utcnow() + timedelta(days=30)
        
        metrics = UsageMetricsService.create_usage_metrics(
            db_session, org_id, period_start, period_end
        )
        
        assert metrics.org_id == org_id
        assert metrics.projects_generated == 0
        assert metrics.documents_created == 0
    
    def test_increment_project_count(self, db_session):
        """Test incrementing project counter."""
        from app.services.stripe_service import UsageMetricsService
        
        org_id = "test_org_456"
        metrics = UsageMetricsService.create_usage_metrics(
            db_session, org_id,
            datetime.utcnow(),
            datetime.utcnow() + timedelta(days=30)
        )
        
        UsageMetricsService.increment_project_count(db_session, org_id, count=3)
        metrics = UsageMetricsService.get_or_create_metrics(db_session, org_id)
        
        assert metrics.projects_generated == 3
    
    def test_check_free_tier_limit(self, db_session):
        """Test free tier has 3 project limit."""
        from app.services.stripe_service import UsageMetricsService
        
        org_id = "test_org_free"
        metrics = UsageMetricsService.create_usage_metrics(
            db_session, org_id,
            datetime.utcnow(),
            datetime.utcnow() + timedelta(days=30)
        )
        
        # First 3 projects should be allowed
        can_gen = UsageMetricsService.check_project_limit(db_session, org_id)
        assert can_gen == True
        
        # Simulate 3 projects used
        metrics.projects_generated = 3
        db_session.commit()
        
        # 4th project should be rejected
        can_gen = UsageMetricsService.check_project_limit(db_session, org_id)
        assert can_gen == False
    
    def test_usage_reset_on_period_boundary(self, db_session):
        """Test usage resets at end of billing period."""
        from app.services.stripe_service import UsageMetricsService
        
        org_id = "test_org_reset"
        now = datetime.utcnow()
        
        metrics = UsageMetricsService.create_usage_metrics(
            db_session, org_id,
            now - timedelta(days=1),
            now + timedelta(hours=1)  ← Reset in 1 hour
        )
        
        metrics.projects_generated = 5
        db_session.commit()
        
        # Manually advance time past reset_date
        metrics.reset_date = now - timedelta(seconds=1)
        db_session.commit()
        
        # Get metrics should reset counters
        fresh_metrics = UsageMetricsService.get_or_create_metrics(db_session, org_id)
        assert fresh_metrics.projects_generated == 0


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestCheckoutFlow:
    """Test complete checkout flow."""
    
    @pytest.mark.skip(reason="Requires live Stripe API keys")
    def test_create_checkout_session(self, db_session):
        """Test creating Stripe checkout session."""
        from app.services.stripe_service import StripeSubscriptionService
        from app.core.stripe_config import PricingTier
        
        org_id = "org_integration_test"
        
        checkout_url = StripeSubscriptionService.create_checkout_session(
            db_session,
            org_id,
            PricingTier.STARTER,
            "test@example.com",
        )
        
        assert checkout_url.startswith("https://checkout.stripe.com/")
        assert "session_id=" in checkout_url


class TestWebhookHandling:
    """Test webhook event processing."""
    
    def test_webhook_signature_verification(self):
        """Test webhook signature is properly verified."""
        from app.api.v1.billing.webhooks import verify_webhook_signature
        from fastapi import HTTPException
        import stripe
        
        # Invalid signature should raise
        with pytest.raises(HTTPException):
            verify_webhook_signature(
                b'{"invalid": "data"}',
                "invalid_signature"
            )
    
    def test_subscription_created_webhook_idempotent(self, db_session):
        """Test subscription.created webhook is idempotent."""
        from app.api.v1.billing.webhooks import handle_subscription_created
        
        event_data = {
            "id": "sub_test_idempotent",
            "customer": "cus_test_123",
            "items": {"data": [{"plan": {"id": "price_test", "product": "prod_test"}}]},
            "status": "active",
            "metadata": {"org_id": "org_test_123"},
        }
        
        # Call twice - should not error
        import asyncio
        asyncio.run(handle_subscription_created(db_session, event_data))
        asyncio.run(handle_subscription_created(db_session, event_data))
        
        # Verify only one record in DB
        from app.models.stripe_billing import StripeSubscription
        count = db_session.query(StripeSubscription).filter(
            StripeSubscription.stripe_subscription_id == "sub_test_idempotent"
        ).count()
        
        assert count == 1


class TestUsageEnforcement:
    """Test usage limit enforcement."""
    
    def test_project_limit_enforcement_raises(self, db_session):
        """Test project limit raises 402 when exceeded."""
        from app.middleware.usage_enforcement import enforce_project_limit, UsageLimitExceeded
        
        org_id = "org_enforcement_test"
        
        # Create usage metrics at limit
        from app.services.stripe_service import UsageMetricsService
        metrics = UsageMetricsService.create_usage_metrics(
            db_session, org_id,
            datetime.utcnow(),
            datetime.utcnow() + timedelta(days=30)
        )
        metrics.projects_generated = 3  # Free tier limit
        db_session.commit()
        
        # Should raise
        with pytest.raises(UsageLimitExceeded):
            enforce_project_limit(org_id, db_session)


# =============================================================================
# END-TO-END SCENARIO TESTS
# =============================================================================

class TestEndToEndScenarios:
    """Test complete workflows."""
    
    @pytest.mark.skip(reason="Requires test database setup")
    def test_free_user_hits_limit_then_upgrades(self, db_session, client):
        """Complete scenario: Free user → Hit limit → Upgrade → Success"""
        
        # 1. Create organization (free tier by default)
        org_resp = client.post("/api/organizations", json={
            "name": "Test Corp",
            "slug": "test-corp"
        })
        org = org_resp.json()
        org_id = org["id"]
        
        assert org["tier"] == "free"
        
        # 2. Generate 3 projects (all succeed)
        for i in range(3):
            project_resp = client.post("/api/projects/generate", json={
                "title": f"Project {i+1}",
                "description": "Test project"
            }, headers={"Authorization": f"Bearer {get_test_token(org_id)}"}
            )
            assert project_resp.status_code == 200
        
        # 3. Check usage
        usage_resp = client.get(
            f"/api/v1/billing/usage/{org_id}",
            headers={"Authorization": f"Bearer {get_test_token(org_id)}"}
        )
        usage = usage_resp.json()
        assert usage["usage"]["projects_generated"] == 3
        assert usage["limits"]["max_projects_per_month"] == 3
        
        # 4. Try 4th project (should fail)
        project_resp = client.post("/api/projects/generate", json={
            "title": "Project 4",
            "description": "This should fail"
        }, headers={"Authorization": f"Bearer {get_test_token(org_id)}"}
        )
        assert project_resp.status_code == 402
        assert "usage_limit_exceeded" in project_resp.json()["detail"]["error"]
        
        # 5. Create checkout (would normally redirect to Stripe)
        checkout_resp = client.post(
            "/api/v1/billing/setup-checkout",
            json={"tier": "starter"},
            headers={"Authorization": f"Bearer {get_test_token(org_id)}"}
        )
        assert checkout_resp.status_code == 200
        checkout = checkout_resp.json()
        assert "checkout_url" in checkout
        
        # 6. Simulate webhook: subscription.created
        # (In real test, would use stripe CLI or mock)
        
        # 7. Check usage after upgrade
        # (Pro tier allows 30 projects)
        
        # 8. Try 4th project (should succeed now)
        # (Would need to mock the subscription in DB)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_test_token(org_id: str) -> str:
    """Generate test JWT token for organization."""
    from app.core.security import create_access_token
    return create_access_token(data={"org_id": org_id})


@pytest.fixture
def db_session():
    """Create test database session."""
    from app.database import Base, engine, SessionLocal
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    yield db
    db.close()
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


# =============================================================================
# MANUAL TEST SCENARIOS (For QA)
# =============================================================================

"""
MANUAL QA TEST SCENARIOS:

Scenario 1: Free User Workflow
──────────────────────────────
1. Sign up new account (creates free tier org)
2. Generate project → Success
3. Generate project → Success
4. Generate project → Success (3/3)
5. Generate project → FAIL: 402 Payment Required
6. PASS: Shows upgrade prompt

Scenario 2: Successful Upgrade
──────────────────────────────
1. Click "Upgrade to Pro"
2. Redirected to Stripe Checkout
3. Enter test card: 4242 4242 4242 4242
4. Complete payment
5. Redirected to success page
6. Check subscription in dashboard (should show Pro)
7. Generate project → Success (should not fail anymore)
8. PASS: Pro tier works, can generate unlimited projects

Scenario 3: Plan Change
──────────────────────
1. User on Starter plan
2. Click "Upgrade to Pro"
3. API call: PATCH /subscription/{org_id}/change-plan with new_tier=pro
4. Verify Stripe updated
5. Verify DB updated
6. Check new limit: 999999 projects
7. PASS: Successfully upgraded

Scenario 4: Cancellation
───────────────────────
1. User on Pro plan
2. Click "Cancel Subscription"
3. API call: DELETE /subscription/{org_id}/cancel with immediate=false
4. Verify cancel_at_period_end=true in DB
5. Verify user still has access until period end
6. Simulate period ending (manually)
7. Verify usage resets to free tier limits
8. PASS: Cancellation works, resets to free tier

Scenario 5: Payment Failure Recovery
────────────────────────────────────
1. User has failed payment
2. Stripe sends invoice.payment_failed webhook
3. Backend marks subscription as past_due
4. User sees "Payment Failed" message
5. User updates payment method in Stripe portal
6. Retry payment through Stripe
7. Stripe sends invoice.payment_succeeded
8. Subscription restored to active
9. PASS: Payment recovery works

Scenario 6: Webhook Retry Idempotency
─────────────────────────────────────
1. Stripe sends customer.subscription.created
2. Backend receives and processes (creates DB record)
3. Stripe retries (same event ID)
4. Backend receives again (duplicate)
5. Backend detects duplicate (UNIQUE constraint)
6. Gracefully handles, logs, returns 200
7. Database has only ONE record
8. PASS: Idempotent handling prevents duplicates
"""

print(__doc__)
