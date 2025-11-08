from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class StochasticReversal(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    minimal_roi = {"0": 0.05}
    stoploss = -0.10
    startup_candle_count: int = 14

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        stoch = ta.STOCH(dataframe,
                         fastk_period=14,
                         slowk_period=3,
                         slowk_matype=0,
                         slowd_period=3,
                         slowd_matype=0)
        dataframe['slowk'] = stoch['slowk']
        dataframe['slowd'] = stoch['slowd']
        return dataframe

    def populate_entry_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['slowk'] < 20) &
                qtpylib.crossed_above(dataframe['slowk'], dataframe['slowd'])
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['slowk'] > 80) &
                qtpylib.crossed_below(dataframe['slowk'], dataframe['slowd'])
            ),
            'exit_long'] = 1
        return dataframe
