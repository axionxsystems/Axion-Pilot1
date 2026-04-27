
# AXION-X — QUICK START GUIDE
## Solo Founder | Start Here Today

---

## YOU HAVE 4 DOCUMENTS

1. **AXION_SCALING_STRATEGY.md** — The full vision and path to $1B
   - What AXIONX is, who it's for, revenue model, moat strategy, fundraising roadmap
   - Read once fully. Revisit when making major decisions.

2. **COPILOT_PROMPTS_READY.md** — The 7 technical blueprints
   - Copy-paste prompts for GitHub Copilot / Claude in VS Code
   - Do NOT use until the relevant milestone gate is reached (see checklist)

3. **IMPLEMENTATION_CHECKLIST.md** — Week-by-week execution
   - Your day-to-day operating document
   - Work top to bottom, do not skip

4. **This file** — Where to start today

---

## TODAY (DAY 1)

Do these 5 things. Nothing else.

**1. Write your ICP sentence (20 minutes)**
Open a notes app and complete this sentence:
> "I help [specific person] who [specific situation] solve [specific problem] and get [specific outcome] — for $[price]/mo."

Example: "I help PhD students who spend 10+ hours writing literature reviews generate a complete, properly structured review in 15 minutes — for $99/mo."

Do not move on until this sentence is specific enough that you could find 100 people on LinkedIn who match it exactly.

**2. Set up your payment infrastructure (30 minutes)**
- Create Stripe account at stripe.com (free)
- Create one payment link at your chosen price ($99 or $199)
- Copy the link — this is how your first customer pays you
- Do not build a checkout page. A Stripe link is enough.

**3. Set up your booking link (10 minutes)**
- Create Cal.com account (free)
- Set up a "20-minute AXIONX Discovery Call" event
- Connect your calendar
- Copy the booking link

**4. Set up your business email (15 minutes)**
- Go to zoho.com/mail
- Create free account with your domain (e.g., thor@axionx.co)
- This makes outreach look credible vs a Gmail address

**5. Find your first 20 prospects (30 minutes)**
- Go to LinkedIn
- Search for people who match your ICP sentence
- Open 20 profiles — people with the specific job title, studying or working in the specific field
- Copy their names into a Notion table with columns: Name | LinkedIn URL | DM Sent | Reply | Call Booked | Paid

**End of Day 1**: You have a payment link, a booking link, a business email, and 20 people to contact tomorrow morning.

---

## THIS WEEK (DAYS 2–5)

**Day 2 — First DMs**
Send the first 10 DMs to your list. Use this template exactly:

```
Hey [Name],

I'm building AXIONX — an AI that generates [specific document type] 
in minutes instead of hours. 

Would you be open to a 20-min call to see if it's useful for your work? 
No pitch, just want to learn from someone in [their field].

[Your name]
```

Short. No links yet. No product description. Just a call request.

Log every DM in your Notion table.

**Day 3 — Follow-ups + Record Demo**
- Follow up on Day 1 DMs with no reply: "Hey [name], just bumping this up in case it got buried!"
- Send 10 more DMs
- Record your Loom demo: 5 minutes, show the exact problem and exactly how AXIONX solves it. No slides — screen recording only.
- Post on LinkedIn: "I'm building [one sentence description of AXIONX]. Here's a 5-min demo: [Loom link]. Would love feedback from anyone in [ICP field]."

**Day 4 — Discovery Call Prep**
If you have any calls booked, prepare:
- Open with: "Tell me how you currently create [document type]"
- Listen for 5+ minutes before showing anything
- Demo only the feature that solves the specific pain they described
- Close with: "This is $[price]/mo. Does that work?" — then stop talking
- If yes: "Great, I'll send you a payment link right now" — send Stripe link in the call chat

If no calls yet, send 10 more DMs and follow up on previous ones.

**Day 5 — Review**
- How many DMs sent total?
- How many replies?
- How many calls booked?
- What is the most common response you're getting?

If replies are low: your ICP sentence isn't specific enough. Rewrite it.
If replies are good but no calls: your DM is too salesy. Shorten it further.
If calls are happening but no closes: you're not uncovering the real pain. Ask more, demo less.

---

## FIRST MONTH TARGETS

```
Week 1: 30+ DMs sent, 3+ discovery calls booked
Week 2: 5+ discovery calls completed, 1+ paying customer
Week 3: $500+ MRR, referral system started
Week 4: $1,000 MRR — MILESTONE 0 COMPLETE
```

The moment you hit $1,000 in Stripe: open IMPLEMENTATION_CHECKLIST.md and start Milestone 1.

---

## YOUR DAILY 3-HOUR RHYTHM

You are an MSc student. You cannot work 12-hour days on this. You don't need to.

```
1 HOUR — MORNING
• Check Stripe (any issues?)
• Reply to all messages from customers and prospects
• Send 5 DMs or follow-ups

1 HOUR — AFTERNOON/EVENING
• Discovery calls (if scheduled)
• Fix any product bug reported today
• One piece of outreach follow-through

1 HOUR — NIGHT
• One LinkedIn post or content piece
• Log the day in Notion
• Write tomorrow's single most important action
```

3 focused hours/day beats 8 scattered hours every time.

---

## WHEN TO ASK YOUR PARTNER FOR HELP

Your partner is available for technical problems but is busy with their own project. Respect their time by coming prepared:

**Before asking, always:**
1. Try to solve it with Claude or Copilot first (paste the error + code and ask)
2. Google the specific error message
3. Check the relevant Copilot Prompt in COPILOT_PROMPTS_READY.md

**Good asks for your partner:**
- "I'm getting this specific error after running Copilot Prompt 1. Here's the full error and the generated code. What am I missing?"
- "Can you review this multi-tenancy implementation for security holes?" (Prompt 4 — security review is worth their time)
- "The Celery workers are crashing on this specific task. Here's the traceback."

**Not good asks:**
- "The app isn't working" (too vague — diagnose first)
- "Can you write the Stripe integration?" (that's what Copilot Prompt 6 is for)
- Anything you could solve in 30 minutes with Claude + Google

**Rule**: Use your partner for the 20% of technical problems that genuinely need human expertise. Use AI tools for the 80% that don't.

---

## THE COPILOT PROMPTS — WHEN TO USE EACH ONE

| Prompt | What It Does | Use At |
|--------|-------------|--------|
| Prompt 1 | PostgreSQL migration | $1K MRR — Milestone 1 |
| Prompt 2 | API v1 restructure | $1K MRR — Milestone 1 |
| Prompt 3 | Auth overhaul (API keys, OAuth, SSO) | $10K MRR — Milestone 2 |
| Prompt 4 | Multi-tenancy (org isolation) | $10K MRR — Milestone 2 |
| Prompt 5 | Celery async job queue | $10K MRR — Milestone 2 |
| Prompt 6 | Stripe billing + usage tracking | $10K MRR — Milestone 2 |
| Prompt 7 | Sentry + monitoring | $10K MRR — Milestone 2 |

Do not use these prompts before the milestone condition is met. Over-engineering before product-market fit is the most common way solo founders waste time.

---

## THE MOST IMPORTANT THING

You want to build a billion-dollar company. That outcome is real and achievable. Here is the only thing standing between you and it:

**Consistency over intensity.**

You don't need a viral launch. You don't need a perfect product. You don't need funding. You need to send DMs every morning, take calls every afternoon, and fix things every evening — for 6 weeks straight without stopping.

The first $1K MRR is the hardest. Once money is moving, everything gets easier. Investors take you seriously. Customers refer others. Your own belief compounds.

**The path is clear. The tools are in your hands. Start today.**

---

## DOCUMENT READING ORDER

First time through:
1. This file (you're here) → gives you Day 1 actions
2. AXION_SCALING_STRATEGY.md → gives you the full vision
3. IMPLEMENTATION_CHECKLIST.md → gives you week-by-week execution
4. COPILOT_PROMPTS_READY.md → use when milestone conditions are met

Daily reference:
- IMPLEMENTATION_CHECKLIST.md → what to do today
- This file → when you need a reset or feel stuck

Major decisions:
- AXION_SCALING_STRATEGY.md → pricing, positioning, fundraising

Technical execution:
- COPILOT_PROMPTS_READY.md → at the right milestone
