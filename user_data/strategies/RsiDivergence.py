from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class RsiDivergence(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    minimal_roi = {"0": 0.05}
    stoploss = -0.10
    startup_candle_count: int = 30 # Lookback period + RSI period

    # Lookback period for divergence detection
    divergence_lookback = 28

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Bullish Divergence:
        # Price makes a lower low, but RSI makes a higher low.
        # This is a simplified implementation comparing current candle to a past candle.
        dataframe.loc[
            (
                (dataframe['rsi'] < 40) &  # Look for divergence in the lower region of RSI
                (dataframe['low'] < dataframe['low'].shift(self.divergence_lookback)) &
                (dataframe['rsi'] > dataframe['rsi'].shift(self.divergence_lookback))
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Bearish Divergence:
        # Price makes a higher high, but RSI makes a lower high.
        dataframe.loc[
            (
                (dataframe['rsi'] > 60) &  # Look for divergence in the upper region of RSI
                (dataframe['high'] > dataframe['high'].shift(self.divergence_lookback)) &
                (dataframe['rsi'] < dataframe['rsi'].shift(self.divergence_lookback))
            ),
            'exit_long'] = 1
        return dataframe
