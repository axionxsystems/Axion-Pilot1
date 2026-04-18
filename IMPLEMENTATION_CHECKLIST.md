# AXIONX — IMPLEMENTATION CHECKLIST
## Solo Founder Edition | Revenue-Gated Execution

> **How to use this**: Work milestone by milestone. Do not jump ahead. Complete every checkbox in the current milestone before touching the next one. The gate at the end of each milestone is a hard stop — no exceptions.

---

## MILESTONE 0 — $0 → $1K MRR
### Timeline: Weeks 1–6 | Budget: $0

---

### WEEK 1: Foundation (Days 1–5)

**Day 1 — ICP & Offer**
- [ ] Write your ICP sentence: "I help [specific person] solve [specific problem] and get [specific outcome] for $[price]/mo"
- [ ] Decide your launch price point ($99/mo or $199/mo recommended — not $29, too cheap to validate)
- [ ] List 20 specific people on LinkedIn who match your ICP exactly (names, not categories)

**Day 2 — Site & Payment**
- [ ] Deploy AXIONX site to Vercel free tier (if not already live)
- [ ] Add waitlist form via Tally (free) to site
- [ ] Set up Stripe account — create one payment link at your chosen price
- [ ] Set up Zoho Mail free — get thor@axionx.co (or your domain) working
- [ ] Set up Cal.com free — booking link for 20-min discovery calls

**Day 3 — Demo**
- [ ] Record a 5-minute Loom demo of AXIONX (free tier — 5 min limit is enough)
- [ ] Write 3-sentence LinkedIn post teasing the product with demo link
- [ ] Post it — do not overthink, just post

**Day 4–5 — First Outreach**
- [ ] Send first 10 LinkedIn DMs to people from your Day 1 list
- [ ] DM template: "Hey [name], I'm building AXIONX — an AI that generates [specific document type] in seconds. Would you be open to a 20-min call to see if it's useful for you? No pitch, just feedback."
- [ ] Log every DM in Notion: Name | Sent | Replied | Called | Paid

**Week 1 success check:**
- [ ] Site live with working payment link
- [ ] 10 DMs sent
- [ ] At least 1 reply received

---

### WEEK 2–3: Discovery Calls & First Close

**Outreach (daily, 1 hour)**
- [ ] Send 5 DMs per day (35+ total by end of Week 3)
- [ ] Follow up every DM with no reply after 3 days — one time only
- [ ] Book at least 5 discovery calls

**Discovery calls (use this structure)**
- [ ] Open: "Tell me about how you currently create [document type]"
- [ ] Dig: "How long does that take? What's frustrating about it?"
- [ ] Demo: Show AXIONX solving exactly that problem
- [ ] Close: "This is $[price]/mo. Does that work for you?" — then stop talking
- [ ] If yes: Send Stripe link in chat immediately, do not wait
- [ ] After call: Note every piece of feedback in Notion regardless of outcome

**Product fixes**
- [ ] Fix every bug or friction point that comes up in calls — same day if possible
- [ ] Do not add new features — fix what breaks the demo

**Week 2–3 success check:**
- [ ] 5+ discovery calls completed
- [ ] At least 1 paying customer ($99–$299 in Stripe)

---

### WEEK 4–6: Reach $1K MRR

**Close more customers**
- [ ] Continue 5 DMs/day
- [ ] Add Reddit outreach: post helpful content in r/PhD, r/consulting, r/productivity — link to demo in comments when relevant
- [ ] Ask every customer after Week 1: "Who else do you know who'd find this useful? Can you intro me?"
- [ ] Collect every intro and treat it like a warm DM (highest conversion rate)

**Pricing test**
- [ ] If closing rate is >50% of calls → raise price by 30%
- [ ] If closing rate is <20% of calls → the offer isn't clear enough, rewrite the ICP sentence

**Customer success**
- [ ] Check in with every paying customer at Day 3 and Day 7
- [ ] Fix any issue they report within 24 hours
- [ ] Ask at Day 7: "What's one thing we could add that would make this 10x more valuable for you?"

**Week 4–6 success check:**
- [ ] 4–10 paying customers
- [ ] $1K+ MRR in Stripe
- [ ] At least 1 customer referral received

---

### MILESTONE 0 GATE ⚡
> **Do not proceed to Milestone 1 actions until you see $1,000/mo in Stripe.**
> No amount of planning, building, or tool-shopping substitutes for this.

---

## MILESTONE 1 — $1K → $10K MRR
### Timeline: Months 2–4 | Budget: $55–80/mo (from revenue)

---

### MONTH 2: Systematize Outreach

**Tools to unlock (in order, from revenue)**
- [ ] Instantly.ai ($30/mo) — set up once you have 2+ customers covering the cost
- [ ] Claude Pro ($20/mo) — accelerates copy, proposals, and using the Copilot prompts
- [ ] Railway backend deploy ($5/mo) — when product needs more reliable hosting than Vercel hobby

**Instantly.ai setup**
- [ ] Connect your business email (Zoho)
- [ ] Warm up email domain for 2 weeks before sending (Instantly handles this automatically)
- [ ] Write 5-email cold sequence — use Claude Pro to draft and iterate
- [ ] Sequence structure: (1) Problem intro, (2) AXIONX solution, (3) Social proof, (4) Demo offer, (5) Last chance
- [ ] Build lead list: use Apollo.io free tier (50 contacts/mo) + LinkedIn Sales Navigator free trial
- [ ] Start sending: 20 emails/day max while domain is warming

**Referral system (formalized)**
- [ ] Add to onboarding: at Day 14, send every customer: "You've been using AXIONX for 2 weeks — who's one person in your network who'd benefit? Happy to give them their first month free if they sign up."
- [ ] Track all referrals in Notion

**LinkedIn content (2x per week)**
- [ ] Post 1: Something you learned from a customer this week
- [ ] Post 2: A before/after showing AXIONX output vs manual effort
- [ ] Goal: 1,000 followers by end of Milestone 1

**Month 2 success check:**
- [ ] Instantly sequences running
- [ ] 15+ customers total
- [ ] $3K+ MRR

---

### MONTH 3: Raise Prices + First B2B Attempt

**Pricing**
- [ ] Raise Starter to $39/mo, Pro to $149/mo — grandfather existing customers
- [ ] Add Teams tier ($299/mo) to the website — even if multi-tenancy isn't fully built yet (waitlist the first teams customers, onboard manually)
- [ ] Add annual pricing option (20% discount) — improves cash flow dramatically

**First B2B outreach**
- [ ] Identify 10 small consulting firms or law firms in your ICP
- [ ] Personalize outreach: reference a specific document type they produce
- [ ] Offer a free 2-week team trial (you onboard them manually)
- [ ] Goal: 1–2 teams customers by end of month ($299/mo each)

**Technical: Start Copilot Prompt 1**
- [ ] Create Supabase account (free tier)
- [ ] Run Copilot Prompt 1 (PostgreSQL migration) — ask partner to review if needed
- [ ] Test migration locally before touching production
- [ ] Keep SQLite in production until migration is verified — do not break what's working

**Month 3 success check:**
- [ ] New pricing live
- [ ] At least 1 Teams customer
- [ ] $5K+ MRR
- [ ] Supabase set up and migration tested locally

---

### MONTH 4: API v1 + Hit $10K

**Technical: Copilot Prompt 2**
- [ ] Run Copilot Prompt 2 (API v1 restructure)
- [ ] Move all routes to /api/v1/ — update frontend API calls
- [ ] Test all endpoints — do not deploy until 100% of existing features still work
- [ ] Add Posthog free tier for product analytics — track which features customers actually use

**Revenue push**
- [ ] Increase Instantly sequences to 40 emails/day
- [ ] Add 2nd LinkedIn content post type: "Week X of building AXIONX" update (builds personal brand and accountability)
- [ ] Reach out to 5 university department heads directly — offer a 10-seat Teams trial
- [ ] Ask every customer for a written testimonial (use on site for social proof)

**Milestone 1 success check:**
- [ ] API v1 live in production
- [ ] Posthog tracking active
- [ ] 30–50 paying customers
- [ ] $10K+ MRR in Stripe

---

### MILESTONE 1 GATE ⚡
> **Do not spend on Auth0, paid ads, or enterprise tooling until you hit $10K MRR.**
> The product-market fit is proven at this point. Now you build the machine.

---

## MILESTONE 2 — $10K → $50K MRR
### Timeline: Months 4–8 | Budget: $300–600/mo (from revenue)

---

### MONTH 5: Multi-Tenancy + Teams Go-Live

**Technical: Copilot Prompts 3 & 4**
- [ ] Run Copilot Prompt 4 (multi-tenancy) — critical for Teams tier to work properly
- [ ] Add org_id to all models
- [ ] Test data isolation: org A cannot see org B's data under any circumstance
- [ ] Run Copilot Prompt 3 (Auth) — add API key authentication for Pro users
- [ ] Ask partner to review multi-tenancy implementation — security is not the place to cut corners

**B2B sales push**
- [ ] Move all Teams waitlist customers onto live multi-tenant product
- [ ] Create a Teams demo flow (separate from individual demo)
- [ ] Target: 5 Teams customers by end of month ($299 each = $1,500 from this tier alone)
- [ ] Add HubSpot free CRM — Notion is too limited once you're managing 50+ customers

**Content**
- [ ] Write first case study: one customer, specific results, before/after numbers
- [ ] Publish on site and LinkedIn
- [ ] Start SEO blog: one article/week targeting "AI document generator for [vertical]"

**Month 5 success check:**
- [ ] Multi-tenancy live and tested
- [ ] 5+ Teams customers
- [ ] $15K+ MRR

---

### MONTH 6: Async Jobs + Integrations

**Technical: Copilot Prompts 5 & 6**
- [ ] Set up Upstash Redis free tier
- [ ] Run Copilot Prompt 5 (Celery async jobs) — stops long document generation from timing out
- [ ] Run Copilot Prompt 6 (Stripe subscriptions) — move from payment links to proper subscriptions
- [ ] Run Copilot Prompt 7 (Sentry monitoring) — you need to know when things break before customers tell you

**Integrations**
- [ ] Submit AXIONX to Zapier app directory (free, 4–6 week review)
- [ ] Add Google Drive export option (saves document directly to Drive)
- [ ] These two unlock passive signups and reduce churn

**Pricing update**
- [ ] Add Auth0 ($23/mo) — Enterprise prospects will ask about SSO at this stage
- [ ] Create Enterprise waitlist page on site — start capturing enterprise interest even before product is ready

**Month 6 success check:**
- [ ] Celery async generation working
- [ ] Stripe subscriptions replacing payment links
- [ ] Sentry active
- [ ] Zapier submission in review
- [ ] $25K+ MRR

---

### MONTHS 7–8: Content Flywheel + First Paid Distribution

**Content at scale**
- [ ] LinkedIn: 3x/week — mix of build updates, customer stories, document automation insights
- [ ] Goal: 5,000 LinkedIn followers by Month 8
- [ ] Collect 5 more customer case studies — ask every customer with good results
- [ ] Submit to G2 and Capterra — ask 10 customers to leave reviews

**First paid content (unlock at $25K MRR)**
- [ ] $100–200/mo LinkedIn sponsored post targeting your ICP
- [ ] Only run ads to content that already converts organically
- [ ] Measure: cost per trial start, trial-to-paid conversion

**Enterprise pipeline**
- [ ] Identify 20 universities with clear document generation pain
- [ ] Personalized outreach from your LinkedIn profile (not cold email — too impersonal for enterprise)
- [ ] Offer: free 30-day pilot for one department, no commitment
- [ ] Goal: 2–3 enterprise pilots by end of Month 8

**Milestone 2 success check:**
- [ ] All 7 Copilot prompts implemented
- [ ] Zapier listing live
- [ ] 5K LinkedIn followers
- [ ] 3–5 case studies on site
- [ ] 100–200 paying customers
- [ ] $50K+ MRR

---

### MILESTONE 2 GATE ⚡
> **Only hire when a role is actively blocking revenue.**
> At $50K MRR you are generating $600K ARR. You now have a fundable story.

---

## MILESTONE 3 — $50K → $100K MRR
### Timeline: Months 8–14 | Budget: $1–3K/mo (from revenue)

---

### MONTHS 8–10: Enterprise + First Hire

**Enterprise sales**
- [ ] Close 3–5 enterprise pilots at $2K–$20K/mo each
- [ ] Document every objection and add it to a FAQ for future sales
- [ ] Build enterprise-specific features customers ask for (SAML, audit logs, IP whitelisting)
- [ ] Create enterprise pricing page with "Contact Sales" CTA

**First hire: Sales (commission-heavy)**
- Hire only when you are turning down meetings due to bandwidth
- [ ] Post role: Base $2–3K/mo + 20% commission on new ARR
- [ ] Hire someone who has sold B2B SaaS before — not a generalist
- [ ] Give them 30 days to close at least 1 deal — if not, wrong hire

**Product Hunt launch**
- [ ] Prepare: 20+ hunter supporters lined up in advance
- [ ] Create launch assets: demo GIF, tagline, description
- [ ] Set launch date when you have 5+ case studies and solid reviews on G2
- [ ] Goal: Top 5 product of the day

**Seed raise preparation**
- [ ] Build 3-year financial model (revenue, costs, headcount)
- [ ] Create investor deck (12 slides max: problem, solution, market, traction, team, ask)
- [ ] Traction slide must show: MRR chart, customer count, NPS, churn rate, enterprise pipeline
- [ ] Apply to YC next batch (applications open twice/year)
- [ ] Identify 20 angels in EdTech/SaaS space on LinkedIn

**Month 8–10 success check:**
- [ ] 3+ enterprise pilots live
- [ ] Product Hunt launched
- [ ] G2 rating: 4.7+
- [ ] Sales hire onboarded
- [ ] Seed deck ready
- [ ] $75K+ MRR

---

### MONTHS 11–14: Close the Seed Round

**Fundraising execution**
- [ ] Send warm intro requests to angels and VCs through LinkedIn connections
- [ ] Run a tight process: first meetings in same 2-week window, term sheet deadline
- [ ] Target: $1–2M on $8–15M valuation
- [ ] Use raised capital to hire: 1 engineer, 1 more sales

**Scale what's working**
- [ ] Double down on whatever channel is producing cheapest CAC
- [ ] If LinkedIn content: post daily, invest in better production
- [ ] If cold email: scale sequences, add more lead sources
- [ ] If referrals: formalize referral program with cash incentive

**Milestone 3 success check:**
- [ ] Seed round closed or in term sheet stage
- [ ] 300–500 customers
- [ ] $100K+ MRR
- [ ] Churn <5%/month
- [ ] NPS >50

---

### MILESTONE 3 GATE ⚡
> **At $100K MRR you have a real company. Seed capital in the bank.**
> Everything from here is execution at scale. Reinvest 15–20% of revenue into growth.

---

## MILESTONE 4 — $100K MRR → Series A Ready
### Timeline: Month 14–24 | Budget: 15–20% of revenue

**This phase runs on Seed capital and revenue. Execution plan is in AXION_SCALING_STRATEGY.md Part 6 (Post-Seed section). Key priorities:**

- [ ] Hire engineering team (2–3 engineers) — product velocity is now the constraint
- [ ] International expansion: UK, Canada, Australia first
- [ ] Platform partnerships: Zapier, Chegg, Coursera outreach
- [ ] Proprietary AI model fine-tuning begins
- [ ] Series A preparation: $1.2M ARR run rate, enterprise logos, 20%+ MoM
- [ ] Template marketplace launch: community-curated, incentivized

---

## DAILY OPERATING RHYTHM (SOLO FOUNDER)

Use this every day until $10K MRR:

```
MORNING (1 hour):
□ Check Stripe dashboard — any churn signals?
□ Reply to customer messages — within 2 hours always
□ Send 5 LinkedIn DMs or 10 cold emails (depending on milestone)

AFTERNOON (1 hour):
□ Discovery calls (if scheduled)
□ Follow up on pending deals
□ Fix any product issues customers reported

EVENING (1 hour):
□ Write one piece of content (LinkedIn post, blog paragraph, case study)
□ Log everything in Notion: deals, feedback, ideas
□ Review: what is the single most important thing to do tomorrow?
```

---

## WEEKLY REVIEW TEMPLATE

Every Sunday, 30 minutes:

```
MRR THIS WEEK: $______  (vs last week: $______)
NEW CUSTOMERS: ___
CHURNED CUSTOMERS: ___
DISCOVERY CALLS HELD: ___
DMs/EMAILS SENT: ___

WHAT WORKED:
- 

WHAT DIDN'T:
- 

SINGLE MOST IMPORTANT ACTION NEXT WEEK:
- 
```

---

## WHEN YOU GET STUCK

**Problem**: Nobody is replying to DMs
**Fix**: Change your ICP sentence. The problem or outcome isn't resonating. Interview 3 existing customers about why they bought — use their exact language in new DMs.

**Problem**: People reply but don't convert on calls
**Fix**: You're not uncovering the real pain. Ask more questions, demo less. The sale happens when they feel understood, not when they see features.

**Problem**: Customers churn after 1 month
**Fix**: Stop selling and start listening. Your product isn't delivering the promised outcome. Talk to churned customers — ask exactly what went wrong.

**Problem**: Partner not available when you need technical help
**Fix**: Document the technical question precisely before asking. Use Claude or Copilot first — 80% of technical blockers can be resolved with AI assistance. Partner is for the 20% that genuinely needs human review.

**Problem**: Copilot generates wrong code
**Fix**: Read the error carefully. Ask Claude: "I got this error: [error]. Here is the relevant code: [code]. What's wrong and how do I fix it?" Be specific — vague questions get vague answers.

**Problem**: Database migration fails in production
**Fix**: Rollback immediately: `alembic downgrade -1`. Reproduce the failure locally. Fix the migration file. Test 3 times locally before re-running in production.

---

## TOOL UNLOCK SCHEDULE (DO NOT DEVIATE)

| Tool | Monthly Cost | Unlock Condition |
|------|-------------|------------------|
| Stripe | 2.9% | Day 1 — free to set up |
| Vercel | $0 | Day 1 |
| Tally | $0 | Day 1 |
| Notion | $0 | Day 1 |
| Cal.com | $0 | Day 1 |
| Zoho Mail | $0 | Day 1 |
| Loom | $0 | Day 1 |
| Railway | $5 | First Stripe payment received |
| Claude Pro | $20 | 2+ paying customers |
| Instantly.ai | $30 | 2+ paying customers |
| Supabase | $0 | $1K MRR |
| Posthog | $0 | $1K MRR |
| HubSpot CRM | $0 | $5K MRR |
| Auth0 | $23 | $10K MRR |
| Upstash Redis | $0 | $10K MRR |
| Sentry | $0 | $10K MRR |
| Apollo Pro | $49 | $25K MRR |
| Pipedrive | $24 | $25K MRR |
| Intercom | $74 | $50K MRR |
| Paid LinkedIn Ads | $100–200 | $25K MRR + proven organic conversion |
| AWS/GCP | $500+ | Post-Seed only |
| Salesforce | $300 | Post-Series A only |
