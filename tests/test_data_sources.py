from vela.fetch_prices import manual_price_snapshot
from vela.fetch_sec_filings import company_facts_url, normalize_cik, submissions_url


def test_normalize_cik_and_sec_urls():
    assert normalize_cik("320193") == "0000320193"
    assert submissions_url("320193").endswith("/CIK0000320193.json")
    assert company_facts_url("320193").endswith("/CIK0000320193.json")


def test_manual_price_snapshot_never_requires_network():
    snapshot = manual_price_snapshot("nvda")
    assert snapshot.ticker == "NVDA"
    assert snapshot.provider == "manual"
    assert snapshot.price is None
