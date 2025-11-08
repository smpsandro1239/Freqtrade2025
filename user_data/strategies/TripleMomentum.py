from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class TripleMomentum(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    minimal_roi = {"0": 0.05}
    stoploss = -0.10
    startup_candle_count: int = 26 # For MACD slow period

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # MACD
        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Stochastic
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
        # Bullish convergence
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal']) &
                (dataframe['rsi'] < 45) & # RSI is not overbought
                qtpylib.crossed_above(dataframe['slowk'], dataframe['slowd']) &
                (dataframe['slowk'] < 30) # Stochastic is in oversold territory
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Bearish convergence
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal']) &
                (dataframe['rsi'] > 55) & # RSI is not oversold
                qtpylib.crossed_below(dataframe['slowk'], dataframe['slowd']) &
                (dataframe['slowk'] > 70) # Stochastic is in overbought territory
            ),
            'exit_long'] = 1
        return dataframe
