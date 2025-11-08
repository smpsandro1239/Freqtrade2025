from freqtrade.strategy import IStrategy
from pandas import DataFrame
import freqtrade.vendor.qtpylib.indicators as qtpylib

class SuperTrend(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    minimal_roi = {"0": 0.05}
    stoploss = -0.10
    startup_candle_count: int = 10  # ATR period

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        st = qtpylib.supertrend(dataframe, period=10, multiplier=3)
        dataframe['supertrend_direction'] = st['stx']
        return dataframe

    def populate_entry_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['supertrend_direction'] == 'up') &
                (dataframe['supertrend_direction'].shift(1) == 'down')
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['supertrend_direction'] == 'down') &
                (dataframe['supertrend_direction'].shift(1) == 'up')
            ),
            'exit_long'] = 1
        return dataframe
