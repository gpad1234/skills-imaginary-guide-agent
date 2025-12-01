## Alternate design: LangChain + LangGraph

This document describes an alternate orchestration design using LangChain
and LangGraph to coordinate calls to the local osquery tools defined in
`mcp_osquery_server/osquery_tools.py`.

When to use
- If you want to use a graph-based planner or visually author flows that
  combine LLM reasoning and tool execution.
- If you plan to integrate richer control logic (conditionals, retries,
  branching) driven by LLM outputs and want to reuse LangChain agent
  patterns.

Key ideas
- Each osquery tool (system_info, processes, users, custom_query, etc.) is
  represented as a node in the graph.
- The LLM (via a LangChain agent or chain) provides inputs or selects which
  nodes to run.
- LangGraph composes nodes and defines edges (data dependencies). The graph
  runtime executes nodes and passes results back to the LLM.

Implementation approach (high-level)
1. Keep the existing `mcp_osquery_server/osquery_tools.py` functions as the
   canonical implementation of system queries. These are plain Python
   callables and remain the single source of truth.
2. Add a small adapter (included in this repo as `langgraph_adapter.py`) that
   maps tool names to callables and produces either a design dictionary or a
   runtime graph when `langchain`/`langgraph` are installed.
3. In a host environment with `langchain` and `langgraph` installed, use the
   adapter output to instantiate a LangGraph graph and wire it into a
   LangChain agent (or custom runtime) that executes nodes based on LLM
   decisions.

Tradeoffs
- Pros:
  - Richer orchestration and easier visual editing of flows.
  - Leverages LangChain ecosystems (memory, tools, agents).
- Cons:
  - Additional runtime dependencies and potential version drift.
  - More surface area for security considerations (LLM-driven actions).

Security and operational notes
- Treat the graph runtime like any other tool runner: validate and sandbox
  inputs from LLMs before executing OS-level commands.
- Use least-privilege when running osquery and keep secrets out of the
  environment; rotate keys in `.env` regularly.

Quick start (developer):
1. pip install -r requirements.txt (or only the extras: `pip install langchain langgraph`)
2. From a Python shell:
   ```python
   from langgraph_adapter import build_langgraph, example_run

   g = build_langgraph()
   example_run(g)
   ```

3. When satisfied, build a runtime graph using your installed versions of
   LangChain/LangGraph and map graph nodes to the callables in
   `mcp_osquery_server.osquery_tools`.

Further reading
- See `docs/ARCHITECTURE.md` for the main architecture and where this
  alternate design fits.
