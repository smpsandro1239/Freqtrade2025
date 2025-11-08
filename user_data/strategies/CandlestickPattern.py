from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class CandlestickPattern(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    minimal_roi = {"0": 0.05}
    stoploss = -0.10
    startup_candle_count: int = 50  # For EMA50

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Trend Indicator
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)

        # Bullish Patterns
        dataframe['cdl_hammer'] = ta.CDLHAMMER(dataframe)
        dataframe['cdl_engulfing_bullish'] = ta.CDLENGULFING(dataframe) > 0
        dataframe['cdl_morningstar'] = ta.CDLMORNINGSTAR(dataframe)

        # Bearish Patterns
        dataframe['cdl_hangingman'] = ta.CDLHANGINGMAN(dataframe)
        dataframe['cdl_engulfing_bearish'] = ta.CDLENGULFING(dataframe) < 0
        dataframe['cdl_eveningstar'] = ta.CDLEVENINGSTAR(dataframe)

        return dataframe

    def populate_entry_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] > dataframe['ema50']) &  # Uptrend
                (
                    (dataframe['cdl_hammer'] > 0) |
                    (dataframe['cdl_engulfing_bullish']) |
                    (dataframe['cdl_morningstar'] > 0)
                )
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] < dataframe['ema50']) & # Downtrend
                (
                    (dataframe['cdl_hangingman'] < 0) |
                    (dataframe['cdl_engulfing_bearish']) |
                    (dataframe['cdl_eveningstar'] < 0)
                )
            ),
            'exit_long'] = 1
        return dataframe
