"""Tests for pure billing/tier configuration logic (no live Stripe needed)."""
import pytest


def test_all_tiers_present():
    from app.core.stripe_config import TIER_CONFIG, PricingTier

    for tier in PricingTier:
        assert tier in TIER_CONFIG, f"Missing tier config for {tier}"


def test_tier_limits_shape():
    from app.core.stripe_config import get_tier_limits, PricingTier

    limits = get_tier_limits(PricingTier.FREE)
    for key in ("max_projects_per_month", "max_documents", "max_api_calls", "max_team_seats"):
        assert key in limits
        assert isinstance(limits[key], int)


def test_free_tier_is_more_limited_than_pro():
    from app.core.stripe_config import get_tier_limits, PricingTier

    free = get_tier_limits(PricingTier.FREE)
    pro = get_tier_limits(PricingTier.PRO)
    assert free["max_projects_per_month"] < pro["max_projects_per_month"]


def test_price_id_lookup_roundtrip():
    from app.core.stripe_config import TIER_CONFIG, PricingTier, get_tier_by_price_id

    price_id = TIER_CONFIG[PricingTier.STARTER]["stripe_price_id"]
    assert get_tier_by_price_id(price_id) == PricingTier.STARTER


def test_unknown_price_id_raises():
    from app.core.stripe_config import get_tier_by_price_id

    with pytest.raises(ValueError):
        get_tier_by_price_id("price_does_not_exist")
