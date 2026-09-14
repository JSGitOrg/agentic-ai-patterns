# 5. Teaching Guide

For instructors running this as a workshop or course module. Assumes
students are comfortable reading Python but have not necessarily used an
LLM API before.

## Suggested format: one 3-hour workshop, or three 1-hour sessions

### Session 1 (45-60 min): Concepts + Patterns 1-2

- Read/discuss [01-agentic-ai-concepts.md](01-agentic-ai-concepts.md)
  together (15 min). Anchor on the four building blocks and the
  "loop with consequences" definition.
- Live-run Pattern 1 (`brand_assistant`) in mock mode, then walk the trace
  line by line: which line is "the model deciding," which line is "your
  code acting"?
- Have students change the question and predict what the mock will do
  before running it (it's scripted, so this is safe and instructive).
- Introduce Pattern 2. Ask: *why can't this be a single tool-calling loop
  like Pattern 1?* (Answer: it could, but you'd be paying an LLM call to
  "decide" something that never varies -- the fixed order is a feature.)

**Checkpoint discussion question:** "Was Pattern 1 or Pattern 2 more
predictable? Which would you trust more in a system that emails a
customer automatically?"

### Session 2 (45-60 min): Patterns 3-5

- Run Pattern 3, and have students watch the trace timestamps to *prove*
  the three translations ran concurrently, not one after another.
- Run Pattern 4. Ask students to predict how many iterations it will take
  before looking at the code (it's designed to take exactly 2).
- Discuss the `MAX_ITERATIONS` safety valve: what happens to cost and
  latency if a critic never approves? Have them find the line that
  prevents that.
- Run Pattern 5 with all three example requests. Ask: "what's the actual
  difference between this and an `if/elif` chain?" Push toward: it
  generalizes past whatever keywords you thought to hard-code, at the
  cost of being harder to guarantee.

**Exercise (15-20 min, pairs):** Have each pair extend Pattern 4's mock
critic to require 3 iterations instead of 2, or extend Pattern 5 with a
fourth specialist (`handoff_to_faq_writer`) and route to it.

### Session 3 (60-90 min): Pattern 6 + Capstone

- Run Pattern 6 with two terminals side by side, projected. Have students
  open `http://localhost:8001/.well-known/agent.json` in a browser
  themselves -- seeing the raw JSON that "agent discovery" produces
  demystifies it fast.
- Ask: "what would have to be true for a completely different team, in a
  different codebase, to call this same illustration agent?" (Answer:
  nothing but this HTTP contract -- that's the point.)
- Read [03-use-case-marketing-studio.md](03-use-case-marketing-studio.md)
  together, then run the capstone live.
- **Main exercise:** pick one item from that doc's "Extending the use
  case" list and implement it. Good defaults for a workshop: #1 (add a
  language) for a quick win, #2 (best-effort illustration) for a more
  interesting design discussion, #3 (route into the studio via Pattern 5)
  for advanced groups.

## Discussion questions to seed throughout

- Which of these six patterns did you already understand from outside
  AI (CI/CD pipelines, thread pools, retry loops, microservices)? What's
  actually new here versus what's just a new vocabulary for something
  familiar?
- Where in the capstone is the model making a genuine judgment call
  (drafting, critiquing) versus where is it just doing deterministic
  work that didn't need an LLM at all (the research/tool-lookup steps)?
  Could any LLM call in this repo be replaced by plain code?
- If the illustration agent were built and owned by a completely
  different company, what would change about how much you trust its
  output? What would you want in its agent card before calling it in
  production (auth? rate limits? a way to know its version?)?
- Every "loop" pattern here (1 and 4) has a hard iteration cap. Why is
  that non-negotiable in a real system, in a way it might not have been
  in traditional software?

## Assessment ideas

- **Code reading:** give students a trace log (like the ones in each
  README) with the code redacted, and ask them to identify which pattern
  produced it and justify why from the trace shape alone (timestamps for
  parallel, repeated critic/reviser calls for the loop, etc.).
- **Design exercise:** describe a new scenario (e.g., a support ticket
  triage system, or a research-paper summarizer with fact-checking) and
  have students map its requirements to patterns the way
  [03-use-case-marketing-studio.md](03-use-case-marketing-studio.md) does
  for Cymbal Stadiums, including which parts should NOT use an LLM at all.
- **Implementation:** have students build a small seventh pattern-adjacent
  exercise from scratch: an agent loop (Pattern 1 shape) whose tool is a
  *different* domain than brand guidelines (weather, a to-do list, a
  calculator) -- tests whether they understood the loop mechanics or just
  memorized this repo's specific tools.

## Common misconceptions to correct early

- **"The model runs the tool."** It doesn't -- it only ever asks, by
  name, for a function to be called. Your process decides whether to
  actually do it. Worth emphasizing before students start giving agents
  tools that do something consequential (send email, spend money, delete
  data).
- **"More agents = more agentic = better."** The capstone deliberately
  uses plain sequential/parallel code for anything that doesn't need
  model judgment. Push back on any student design that routes everything
  through an LLM "to be safe."
- **"A2A and MCP are the same thing."** See the callout in
  [01-agentic-ai-concepts.md](01-agentic-ai-concepts.md) -- MCP is
  agent-to-tool, A2A is agent-to-agent. Both matter; they're not
  interchangeable.
