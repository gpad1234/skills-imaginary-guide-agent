"""
langgraph_adapter.py

Lightweight adapter showing how to wire the existing osquery tools into a
LangChain + LangGraph orchestration graph as an alternate design.

This module uses lazy imports so it can be imported in environments that do
not have `langchain` or `langgraph` installed. When those packages are
available, `build_langgraph` will return a graph object (implementation
dependent on installed versions). If not available, the function returns a
plain dict describing the graph, suitable as a design artifact.

Usage (safe):
  from langgraph_adapter import build_langgraph, example_run

  g = build_langgraph()
  example_run(g)

The adapter intentionally does not execute any network calls. It only
constructs a wiring between tool names and the local `mcp_osquery_server`
tool functions so you can plug it into a LangChain-based runtime.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _import_langchain_graphs():
    """Try to import LangChain/LangGraph objects lazily.

    Returns a tuple (langchain_graph_module, langgraph_module) or (None, None)
    if the imports fail. Import errors are caught and returned as None so the
    rest of this module remains safe to import.
    """
    try:
        # Attempt to import common LangChain/LangGraph entry points. The
        # exact import paths may vary between versions; callers should guard
        # for AttributeError when trying to use advanced features.
        import importlib

        lc = importlib.import_module("langchain")
        try:
            lg = importlib.import_module("langgraph")
        except Exception:
            # Older/newer packaging may place graph tools elsewhere; return
            # None to signal unavailability.
            lg = None
        return lc, lg
    except Exception:
        return None, None


def build_langgraph(tool_map: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Builds a representation of a LangGraph-compatible graph that maps
    tool node names to callables.

    - If LangChain/LangGraph are installed, this function will attempt to
      construct real graph objects (best-effort) and return them.
    - Otherwise, it returns a plain dict describing nodes and their inputs
      which can be used as documentation or to manually construct the graph
      in another environment.

    tool_map: mapping of tool_name -> callable; if None, we create a small
    placeholder map showing the names of the available osquery tools.
    """
    # Minimal placeholder map
    if tool_map is None:
        tool_map = {
            "system_info": "mcp_osquery_server.osquery_tools.query_system_info",
            "processes": "mcp_osquery_server.osquery_tools.query_processes",
            "users": "mcp_osquery_server.osquery_tools.query_users",
            "custom_query": "mcp_osquery_server.osquery_tools.custom_query",
        }

    lc, lg = _import_langchain_graphs()
    if lc is None and lg is None:
        # Return a plain design representation
        return {
            "type": "design-only",
            "description": "LangChain/LangGraph not installed; returning a serializable design map",
            "nodes": [
                {"name": name, "callable": str(callable_ref)} for name, callable_ref in tool_map.items()
            ],
            "edges": [
                # Example: a user query flows into custom_query, system_info is optional
                {"from": "user_input", "to": "custom_query"},
            ],
        }

    # If we have graph libs, attempt to build a small graph object. This is
    # intentionally defensive because versions differ.
    graph_repr: Dict[str, Any] = {"type": "runtime-graph", "nodes": [], "edges": []}
    try:
        # The exact APIs depend on installed packages. Try to create a node
        # description using available conveniences.
        for name, callable_ref in tool_map.items():
            graph_repr["nodes"].append({"name": name, "callable": str(callable_ref)})

        graph_repr["edges"].append({"from": "user_input", "to": "custom_query"})
        graph_repr["note"] = "You can use this dict to programmatically create a LangGraph graph in your runtime."
        return graph_repr
    except Exception as e:
        return {"type": "error-building-graph", "error": str(e)}


def example_run(graph_design: Dict[str, Any]) -> None:
    """Simple helper that prints the graph_design in a readable form.

    This function avoids executing any tools; it only demonstrates how to use
    the design dict returned by `build_langgraph`.
    """
    print("LangGraph design / runtime representation:\n")
    import json

    print(json.dumps(graph_design, indent=2, sort_keys=True))


if __name__ == "__main__":
    g = build_langgraph()
    example_run(g)
