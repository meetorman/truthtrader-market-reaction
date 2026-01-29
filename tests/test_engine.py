"""
Tests for market reaction engine.
"""

import pytest
from datetime import datetime, timezone

from market_reaction import (
    get_all_symbols,
    get_symbols_by_sector,
    get_sector_for_symbol,
    get_ticker_info,
    VALID_SECTORS,
    REACTION_WINDOWS,
)


class TestUniverse:
    """Tests for universe functions."""

    def test_get_all_symbols_returns_list(self):
        """Should return a list of symbols."""
        symbols = get_all_symbols()
        assert isinstance(symbols, list)
        assert len(symbols) > 100  # Should have many symbols

    def test_get_all_symbols_contains_major_stocks(self):
        """Should contain major stocks."""
        symbols = get_all_symbols()
        assert "AAPL" in symbols
        assert "MSFT" in symbols
        assert "NVDA" in symbols
        assert "SPY" in symbols

    def test_get_symbols_by_sector_technology(self):
        """Should return tech stocks for technology sector."""
        tech = get_symbols_by_sector("technology")
        assert isinstance(tech, list)
        assert "AAPL" in tech
        assert "NVDA" in tech
        assert "AMD" in tech

    def test_get_symbols_by_sector_financials(self):
        """Should return financial stocks."""
        financials = get_symbols_by_sector("financials")
        assert "JPM" in financials
        assert "BAC" in financials
        assert "V" in financials

    def test_get_symbols_by_sector_unknown(self):
        """Should return empty list for unknown sector."""
        unknown = get_symbols_by_sector("unknown_sector")
        assert unknown == []

    def test_get_sector_for_symbol(self):
        """Should return correct sector for symbol."""
        assert get_sector_for_symbol("AAPL") == "technology"
        assert get_sector_for_symbol("JPM") == "financials"
        assert get_sector_for_symbol("XOM") == "energy"
        assert get_sector_for_symbol("SPY") == "index"

    def test_get_sector_for_symbol_case_insensitive(self):
        """Should be case insensitive."""
        assert get_sector_for_symbol("aapl") == "technology"
        assert get_sector_for_symbol("Aapl") == "technology"

    def test_get_sector_for_unknown_symbol(self):
        """Should return None for unknown symbol."""
        assert get_sector_for_symbol("UNKNOWN123") is None

    def test_get_ticker_info(self):
        """Should return full ticker info."""
        info = get_ticker_info("NVDA")
        assert info is not None
        assert info["symbol"] == "NVDA"
        assert info["sector"] == "technology"
        assert "NVIDIA" in info["name"]

    def test_get_ticker_info_unknown(self):
        """Should return None for unknown ticker."""
        info = get_ticker_info("UNKNOWN123")
        assert info is None


class TestConstants:
    """Tests for constants."""

    def test_valid_sectors_contains_major_sectors(self):
        """Should contain major sectors."""
        assert "technology" in VALID_SECTORS
        assert "financials" in VALID_SECTORS
        assert "healthcare" in VALID_SECTORS
        assert "energy" in VALID_SECTORS

    def test_reaction_windows_contains_standard_windows(self):
        """Should contain standard time windows."""
        assert "1m" in REACTION_WINDOWS
        assert "5m" in REACTION_WINDOWS
        assert "15m" in REACTION_WINDOWS
        assert "1h" in REACTION_WINDOWS
        assert "1d" in REACTION_WINDOWS

    def test_reaction_windows_values_in_minutes(self):
        """Window values should be in minutes."""
        assert REACTION_WINDOWS["1m"] == 1
        assert REACTION_WINDOWS["5m"] == 5
        assert REACTION_WINDOWS["1h"] == 60
        assert REACTION_WINDOWS["1d"] == 1440


class TestGetMarketReaction:
    """Tests for get_market_reaction function."""

    def test_requires_barvault_config(self):
        """Should raise if barvault_config not provided."""
        from market_reaction import get_market_reaction

        with pytest.raises(ValueError, match="barvault_config is required"):
            get_market_reaction(
                event_datetime=datetime(2025, 1, 15, 14, 30, tzinfo=timezone.utc),
                tickers=["TSLA"],
            )

    def test_validates_include_biggest_movers(self):
        """Should raise for invalid include_biggest_movers."""
        from market_reaction import get_market_reaction
        from market_data import ArchiveConfig

        config = ArchiveConfig.local(root="/tmp/test")

        with pytest.raises(ValueError, match="Invalid include_biggest_movers"):
            get_market_reaction(
                event_datetime=datetime(2025, 1, 15, 14, 30, tzinfo=timezone.utc),
                tickers=["TSLA"],
                include_biggest_movers="invalid_sector",
                barvault_config=config,
            )
