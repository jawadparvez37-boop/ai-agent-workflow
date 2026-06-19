from typing import TypedDict

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from app.config import settings
from app.tools import calculate_total, list_invoices, lookup_account

TOOLS = [lookup_account, list_invoices, calculate_total]


class AgentState(TypedDict):
    messages: list


def _should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END


def build_graph():
    model = ChatOpenAI(model=settings.chat_model, temperature=0, api_key=settings.openai_api_key)
    model_with_tools = model.bind_tools(TOOLS)

    def call_model(state: AgentState):
        response = model_with_tools.invoke(state["messages"])
        return {"messages": state["messages"] + [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", _should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


def run_task(task: str) -> dict:
    app = build_graph()
    result = app.invoke({"messages": [HumanMessage(content=task)]})
    messages = result["messages"]

    steps = []
    final = ""
    for msg in messages:
        if getattr(msg, "tool_calls", None):
            for call in msg.tool_calls:
                steps.append({"tool": call["name"], "args": call["args"]})
        if isinstance(msg, ToolMessage):
            steps.append({"tool_result": msg.name, "output": msg.content})
        if msg.type == "ai" and msg.content and not getattr(msg, "tool_calls", None):
            final = msg.content

    return {"task": task, "steps": steps, "result": final}


def run_task_safe(task: str) -> dict:
    try:
        payload = run_task(task)
        payload["status"] = "completed"
        return payload
    except Exception as exc:
        return {
            "task": task,
            "status": "failed",
            "error": str(exc),
            "steps": [],
            "result": "",
        }
