import pytest
from bot.services.nlp import classify_state, analyze_sentiment
from bot.utils.helpers import detect_stress_type

def test_classify_state():
    assert classify_state("я очень тревожусь") == "anxiety"
    assert classify_state("у меня стресс на работе") == "stress"
    assert classify_state("грустно сегодня") == "sadness"
    assert classify_state("привет") == "general"

def test_analyze_sentiment():
    # Реальный вызов модели (может быть медленным, при желании замокать)
    sentiment = analyze_sentiment("я счастлив")
    assert sentiment in ['positive', 'negative', 'neutral']