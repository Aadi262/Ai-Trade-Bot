from typing import Any
from typing_extensions import TypedDict
import structlog
from langgraph.graph import END, StateGraph
from app.agents.base import AgentOutput
from app.agents.bull_researcher import BullResearcher
from app.agents.bear_researcher import BearResearcher
from app.agents.fundamentals import FundamentalsAgent
from app.agents.fund_manager import FundManager
from app.agents.macro import MacroAgent
from app.agents.risk_manager import RiskDecision, RiskManager
from app.agents.sentiment import SentimentAgent
from app.agents.technical import TechnicalAgent
from app.agents.trader import TraderAgent

logger = structlog.get_logger(__name__)

AGENT_CONFIG = {
    "fundamentals":    {"llm": "claude-haiku-4-5-20251001", "max_tokens": 1000},
    "sentiment":       {"llm": "claude-haiku-4-5-20251001", "max_tokens": 800},
    "technical":       {"llm": "claude-haiku-4-5-20251001", "max_tokens": 800},
    "macro":           {"llm": "claude-haiku-4-5-20251001", "max_tokens": 800},
    "bull_researcher": {"llm": "claude-sonnet-4-6", "max_tokens": 2000},
    "bear_researcher": {"llm": "claude-sonnet-4-6", "max_tokens": 2000},
    "trader":          {"llm": "claude-sonnet-4-6", "max_tokens": 1500},
    "fund_manager":    {"llm": "claude-sonnet-4-6", "max_tokens": 800},
    "max_debate_rounds": 2,
    "confidence_threshold": 0.65,
}


class TradingState(TypedDict, total=False):
    symbol: str
    agent_outputs: dict[str, AgentOutput]
    context: dict[str, Any]
    risk_decision: RiskDecision | None
    final_signal: str
    final_confidence: float
    error: str | None


async def run_fundamentals(state: TradingState) -> dict:
    agent = FundamentalsAgent()
    outputs = dict(state.get("agent_outputs", {}))
    ctx = dict(state.get("context", {}))
    try:
        output = await agent.analyze(state["symbol"], ctx)
        outputs["fundamentals"] = output
        ctx["fundamentals"] = output.model_dump()
    except Exception as e:
        logger.error("fundamentals_agent_error", symbol=state["symbol"], error=str(e))
    return {"agent_outputs": outputs, "context": ctx}


async def run_sentiment(state: TradingState) -> dict:
    agent = SentimentAgent()
    outputs = dict(state.get("agent_outputs", {}))
    ctx = dict(state.get("context", {}))
    try:
        output = await agent.analyze(state["symbol"], ctx)
        outputs["sentiment"] = output
        ctx["sentiment"] = output.model_dump()
    except Exception as e:
        logger.error("sentiment_agent_error", symbol=state["symbol"], error=str(e))
    return {"agent_outputs": outputs, "context": ctx}


async def run_technical(state: TradingState) -> dict:
    agent = TechnicalAgent()
    outputs = dict(state.get("agent_outputs", {}))
    ctx = dict(state.get("context", {}))
    try:
        output = await agent.analyze(state["symbol"], ctx)
        outputs["technical"] = output
        ctx["technical"] = output.model_dump()
    except Exception as e:
        logger.error("technical_agent_error", symbol=state["symbol"], error=str(e))
    return {"agent_outputs": outputs, "context": ctx}


async def run_macro(state: TradingState) -> dict:
    agent = MacroAgent()
    outputs = dict(state.get("agent_outputs", {}))
    ctx = dict(state.get("context", {}))
    try:
        output = await agent.analyze(state["symbol"], ctx)
        outputs["macro"] = output
        ctx["macro"] = output.model_dump()
    except Exception as e:
        logger.error("macro_agent_error", symbol=state["symbol"], error=str(e))
    return {"agent_outputs": outputs, "context": ctx}


async def run_researchers(state: TradingState) -> dict:
    bull = BullResearcher()
    bear = BearResearcher()
    outputs = dict(state.get("agent_outputs", {}))
    ctx = dict(state.get("context", {}))
    try:
        bull_out = await bull.analyze(state["symbol"], ctx)
        outputs["bull_researcher"] = bull_out
        ctx["bull_case"] = bull_out.model_dump()
    except Exception as e:
        logger.error("bull_researcher_error", error=str(e))
    try:
        bear_out = await bear.analyze(state["symbol"], ctx)
        outputs["bear_researcher"] = bear_out
        ctx["bear_case"] = bear_out.model_dump()
    except Exception as e:
        logger.error("bear_researcher_error", error=str(e))
    return {"agent_outputs": outputs, "context": ctx}


async def run_trader(state: TradingState) -> dict:
    agent = TraderAgent()
    outputs = dict(state.get("agent_outputs", {}))
    ctx = dict(state.get("context", {}))
    try:
        output = await agent.analyze(state["symbol"], ctx)
        outputs["trader"] = output
        ctx["trader"] = output.model_dump()
    except Exception as e:
        logger.error("trader_agent_error", error=str(e))
    return {"agent_outputs": outputs, "context": ctx}


async def run_fund_manager(state: TradingState) -> dict:
    agent = FundManager()
    outputs = dict(state.get("agent_outputs", {}))
    ctx = dict(state.get("context", {}))
    final_signal = "SKIP"
    final_confidence = 0.0
    try:
        output = await agent.analyze(state["symbol"], ctx)
        outputs["fund_manager"] = output
        final_signal = output.signal
        final_confidence = output.confidence
    except Exception as e:
        logger.error("fund_manager_error", error=str(e))
    return {"agent_outputs": outputs, "final_signal": final_signal, "final_confidence": final_confidence}


def create_graph() -> StateGraph:
    workflow = StateGraph(TradingState)
    workflow.add_node("fundamentals", run_fundamentals)
    workflow.add_node("sentiment", run_sentiment)
    workflow.add_node("technical", run_technical)
    workflow.add_node("macro", run_macro)
    workflow.add_node("researchers", run_researchers)
    workflow.add_node("trader", run_trader)
    workflow.add_node("fund_manager", run_fund_manager)
    workflow.set_entry_point("fundamentals")
    workflow.add_edge("fundamentals", "sentiment")
    workflow.add_edge("sentiment", "technical")
    workflow.add_edge("technical", "macro")
    workflow.add_edge("macro", "researchers")
    workflow.add_edge("researchers", "trader")
    workflow.add_edge("trader", "fund_manager")
    workflow.add_edge("fund_manager", END)
    return workflow.compile()


trading_graph = create_graph()


async def run_pipeline(symbol: str) -> TradingState:
    logger.info("pipeline_started", symbol=symbol)
    initial_state: TradingState = {
        "symbol": symbol,
        "agent_outputs": {},
        "context": {},
        "final_signal": "SKIP",
        "final_confidence": 0.0,
    }
    final_state: TradingState = await trading_graph.ainvoke(initial_state)
    logger.info("pipeline_completed", symbol=symbol,
                signal=final_state.get("final_signal", "SKIP"),
                confidence=final_state.get("final_confidence", 0.0))
    return final_state
