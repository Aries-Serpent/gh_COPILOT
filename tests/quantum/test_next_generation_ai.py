from quantum.next_generation_ai import NextGenerationAI


def test_next_generation_ai_fallback():
    ai = NextGenerationAI(use_quantum=True, backend="hardware")
    result = ai.analyze([1.0, 2.0, 3.0])
    assert result["mode"].startswith("quantum")
    assert isinstance(result["result"], float)
