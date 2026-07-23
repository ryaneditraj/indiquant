"""Data provider plugins."""

from quant_os_api.plugins.data.bse_historical import BSEHistoricalProvider
from quant_os_api.plugins.data.fixture import FixtureDataProvider
from quant_os_api.plugins.data.nse_historical import NSEHistoricalProvider
from quant_os_api.plugins.data.protocol import DataProvider

__all__ = [
    "DataProvider",
    "FixtureDataProvider",
    "NSEHistoricalProvider",
    "BSEHistoricalProvider",
]
