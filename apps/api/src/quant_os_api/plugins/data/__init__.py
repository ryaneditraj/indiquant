"""Data provider plugins."""

from quant_os_api.plugins.data.fixture import FixtureDataProvider
from quant_os_api.plugins.data.protocol import DataProvider

__all__ = ["DataProvider", "FixtureDataProvider"]
