# Import every model module so SQLAlchemy's Base.metadata sees all tables
# before Base.metadata.create_all() runs. Add new model modules here — this
# is the single place that guarantees a new model isn't silently missing
# its table (previously this was done by hand in main.py and easy to forget).
from app.models import user  # noqa: F401
from app.models import project  # noqa: F401
from app.models import settings  # noqa: F401
from app.models import activity  # noqa: F401
from app.models import passkey  # noqa: F401
from app.models import api_key  # noqa: F401
from app.models import rate_limit  # noqa: F401
from app.models import organization  # noqa: F401 — Organization, Subscription, AuditLog
from app.models import branding  # noqa: F401 — OrgBranding
from app.models import analytics  # noqa: F401 — analytics and usage models
from app.models import stripe_billing  # noqa: F401 — Stripe billing models
from app.models import job  # noqa: F401
from app.models import sso  # noqa: F401 — SSOConfig, SSOSession
from app.models import collaboration  # noqa: F401 — Team, TeamMember, ProjectShare, Comment
