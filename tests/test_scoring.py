import pytest

from vela.score_ticker import build_scorecard, scorecard_to_markdown, suggest_label


def test_suggest_label_fails_to_etf_only_when_vwce_test_fails():
    assert suggest_label(60, vwce_alternative_test=False) == "ETF-only is better"


def test_build_scorecard_validates_scores():
    with pytest.raises(ValueError, match="between 0 and 10"):
        build_scorecard(
            business_quality=11,
            financial_strength=5,
            valuation_attractiveness=5,
            growth_durability=5,
            downside_risk=5,
            portfolio_fit=5,
            vwce_alternative_test=True,
        )


def test_build_scorecard_blocks_candidate_when_vwce_test_fails():
    with pytest.raises(ValueError, match="failed VWCE"):
        build_scorecard(
            business_quality=10,
            financial_strength=10,
            valuation_attractiveness=10,
            growth_durability=10,
            downside_risk=10,
            portfolio_fit=10,
            vwce_alternative_test=False,
            final_label="Small position candidate",
        )


def test_scorecard_markdown_contains_final_label():
    scorecard = build_scorecard(
        business_quality=8,
        financial_strength=8,
        valuation_attractiveness=7,
        growth_durability=8,
        downside_risk=7,
        portfolio_fit=7,
        vwce_alternative_test=True,
    )

    markdown = scorecard_to_markdown(scorecard)

    assert "Final label" in markdown
    assert "Watchlist" in markdown
