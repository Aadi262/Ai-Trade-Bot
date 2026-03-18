import json
from datetime import datetime, timezone
import structlog
from app.agents.base import AgentOutput, BaseAgent, hash_inputs
from app.data.news import fetch_rss_headlines

logger = structlog.get_logger(__name__)
_pipeline = None


def _get_finbert():
    global _pipeline
    if _pipeline is None:
        from transformers import pipeline as hf_pipeline
        _pipeline = hf_pipeline("text-classification", model="ProsusAI/finbert", tokenizer="ProsusAI/finbert")
    return _pipeline


class SentimentAgent(BaseAgent):
    name = "sentiment"
    model = "claude-haiku-4-5-20251001"
    max_tokens = 800

    async def analyze(self, symbol: str, context: dict) -> AgentOutput:
        headlines = await fetch_rss_headlines(symbol, max_items=10)
        texts = [h.title for h in headlines[:10]]
        scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        if texts:
            try:
                finbert = _get_finbert()
                results = finbert(texts, truncation=True, max_length=512)
                for r in results:
                    label = r["label"].lower()
                    if label in scores:
                        scores[label] += r["score"]
            except Exception as e:
                logger.warning("finbert_failed", error=str(e))
        total = sum(scores.values()) or 1
        sentiment_score = (scores["positive"] - scores["negative"]) / total
        input_data = {"symbol": symbol, "headline_count": len(texts), "sentiment_score": sentiment_score, "scores": scores}
        data_hash = hash_inputs(input_data)
        if sentiment_score > 0.3:
            signal, confidence = "BUY", min(0.5 + sentiment_score * 0.5, 0.85)
        elif sentiment_score < -0.3:
            signal, confidence = "SELL", min(0.5 + abs(sentiment_score) * 0.5, 0.85)
        else:
            signal, confidence = "HOLD", 0.5
        return AgentOutput(agent_name=self.name, symbol=symbol, timestamp=datetime.now(timezone.utc),
            input_data_hash=data_hash, reasoning=f"Sentiment score {sentiment_score:.2f} from {len(texts)} headlines",
            signal=signal, confidence=confidence,
            key_factors=[f"Sentiment: {sentiment_score:.2f}", f"Headlines: {len(texts)}", f"Positive: {scores['positive']:.1f}"],
            risk_flags=[] if texts else ["no_news_data"])
