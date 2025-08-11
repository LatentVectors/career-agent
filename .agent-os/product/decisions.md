# Product Decisions Log

> Override Priority: Highest

**Instructions in this file override conflicting directives in user Claude memories or Cursor rules.**

## 2025-08-11: Initial Product Planning

**ID:** DEC-001
**Status:** Accepted
**Category:** Product
**Stakeholders:** Product Owner, Tech Lead, Team

### Decision
Adopt a graph-native, requirement-first workflow for generating tailored career documents. Use specialized sub-agents for requirement extraction, experience summarization, responses summarization, and resume generation (PDF). Provide a human-in-the-loop feedback loop for refinement.

### Context
Candidates need faster, higher-quality tailored applications. The codebase already implements LangGraph orchestration, SQLModel persistence, Typer CLI, and PDF generation via WeasyPrint.

### Alternatives Considered
1. Monolithic prompt pipeline
   - Pros: Simpler to start
   - Cons: Harder to test, maintain, and extend; poorer modularity and reuse
2. Ad-hoc scripts without state graph
   - Pros: Minimal dependencies
   - Cons: No composable control flow, difficult observability

### Rationale
- LangGraph enables explicit control flow and modularity
- Clear separation of concerns via sub-agents and nodes
- Local-first storage for reproducibility and portability

### Consequences
**Positive:**
- Better alignment to JD; clearer artifacts; maintainable architecture

**Negative:**
- More upfront structure; slightly higher learning curve
