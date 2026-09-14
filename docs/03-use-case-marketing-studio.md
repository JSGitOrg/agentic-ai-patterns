# 3. The Use Case: Cymbal Stadiums Marketing Content Studio

## The company (fictional, for the training)

**Cymbal Stadiums** runs facility maintenance for 40 stadiums. Its small
communications team is constantly asked, by every department, to turn a
one-line idea ("we should tell people about our training program") into
finished content -- slide copy for a leadership deck, a social post, a
press release, an internal memo -- always on-brand, often needed in
several languages, and usually paired with an illustration.

Today, one person does all of that by hand: look up the brand guide,
draft copy, get it reviewed, translate it, brief a designer for a poster.
It's slow, inconsistent, and doesn't scale past the current team's
headcount.

## Why this is a *good* teaching use case for agentic AI

- **It's not a toy.** Every stage is something a real team actually does,
  today, without AI. Students can immediately map each pattern back to a
  job they already understand.
- **It genuinely needs more than one pattern.** Drafting benefits from a
  fixed pipeline (Pattern 2). Quality control needs iteration (Pattern
  4). Localization is naturally parallel (Pattern 3). Illustration is a
  distinct specialty that should be able to evolve independently (Pattern
  6). Routing different *kinds* of requests needs runtime judgment
  (Pattern 5). None of it needs to be forced.
- **It has a visible failure mode to discuss.** If the illustration agent
  is down, should the whole request fail, or should the studio still ship
  the text? That's a real product decision, not a coding exercise --
  good discussion fodder (see the teaching guide).
- **It's cheap and safe to run.** No real customer data, no real
  spend-sensitive actions (sending emails, making purchases) -- ideal for
  a classroom where many students are running this for the first time.

## Requirements -> patterns

| Requirement | Pattern used | Why this one |
|---|---|---|
| Ground the copy in real brand rules and the right audience, not the model's imagination | Tools (Pattern 1's core idea, reused in Pattern 2) | The model can't invent brand colors from nothing -- it has to look them up |
| Research always happens before writing | Sequential (Pattern 2) | Fixed, always-true dependency |
| First drafts are rarely on-brand enough to ship | Loop critic/reviser (Pattern 4) | Needs iteration, but boundedly -- no infinite back-and-forth |
| Ship in Spanish, French, and German without tripling the wait | Parallel fan-out (Pattern 3) | The three translations don't depend on each other |
| The illustration team should be able to swap in a real image model, or scale independently, without redeploying the writing pipeline | Agent-to-agent over HTTP (Pattern 6) | Genuine ownership/deployment boundary |
| Route requests that aren't slide copy (a quick social post, a press release, an internal memo) to the right specialist | Dynamic routing (Pattern 5) | The *kind* of request varies and isn't known in advance |

## The capstone pipeline

See [`capstone/marketing_content_studio/README.md`](../capstone/marketing_content_studio/README.md)
for how to run it, and the diagram there for the full data flow. In one
sentence: **raw topic -> sequential draft -> loop until on-brand ->
parallel localize + remote illustrate -> a finished content package**.

## Extending the use case (good workshop exercises)

Roughly ordered easy -> hard:

1. Add a fourth language to the parallel fan-out.
2. Make the illustration call best-effort: if it fails, still return the
   text and note the poster is missing, instead of raising.
3. Put Pattern 5's router in front of the studio, so `studio.run()` is
   just one of the specialists an orchestrator can hand off to (alongside
   the social/press/memo writers already in Pattern 5).
4. Replace the mock critic's `"wrench" in draft.lower()` check with a
   structured verdict (ask the model for `{"approved": bool, "feedback":
   str}` as JSON) and parse it properly instead of string-matching a
   prefix.
5. Swap `common/svg_poster.py` for a real image-generation API call
   inside the illustration agent -- and notice that nothing in
   `studio.py` has to change, because the HTTP contract didn't change.
6. Add a second remote agent (e.g. a "compliance checker" that flags
   restricted words) and call it the same way as the illustration agent.

Next: [04-setup-and-running.md](04-setup-and-running.md) to get everything
running.
