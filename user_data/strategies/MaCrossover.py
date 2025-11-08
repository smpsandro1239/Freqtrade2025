from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class MaCrossover(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    minimal_roi = {"0": 0.05}
    stoploss = -0.10
    startup_candle_count: int = 21

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema9'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)
        return dataframe

    def populate_entry_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['ema9'] > dataframe['ema21']) &  # Compra
            (dataframe['ema9'].shift(1) <= dataframe['ema21'].shift(1)),
            'enter_long'] = 1
        return dataframe

    def populate_exit_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['ema9'] < dataframe['ema21']) &  # Venda
            (dataframe['ema9'].shift(1) >= dataframe['ema21'].shift(1)),
            'exit_long'] = 1
        return dataframe

    def custom_stoploss(self, pair: str, trade, current_time, current_rate, current_profit, **kwargs) -> float:
        return -0.02  # Stop loss custom
