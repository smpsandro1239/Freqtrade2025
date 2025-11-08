from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import pandas as pd
import freqtrade.vendor.qtpylib.indicators as qtpylib

class VwapStrategy(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = '5m'
    minimal_roi = {"0": 0.05}
    stoploss = -0.10
    startup_candle_count: int = 30

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # VWAP must be calculated per day.
        # Ensure date column is of datetime type
        if not pd.api.types.is_datetime64_ns_dtype(dataframe['date']):
            dataframe['date'] = pd.to_datetime(dataframe['date'], unit='s')

        # Create a temporary column for Volume * Typical Price
        dataframe['vp'] = ((dataframe['high'] + dataframe['low'] + dataframe['close']) / 3) * dataframe['volume']

        # Group by date and calculate cumulative sums
        day_groups = dataframe.groupby(dataframe['date'].dt.date)
        cum_vol = day_groups['volume'].cumsum()
        cum_vp = day_groups['vp'].cumsum()

        # Calculate VWAP
        dataframe['vwap'] = cum_vp / cum_vol

        # VWAP Bands
        dataframe['vwap_upper'] = dataframe['vwap'] * 1.005
        dataframe['vwap_lower'] = dataframe['vwap'] * 0.995

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Clean up intermediate column
        dataframe.drop(columns=['vp'], inplace=True)

        return dataframe

    def populate_entry_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Buy on pullback to VWAP in an uptrend
        dataframe.loc[
            (
                (dataframe['rsi'] > 50) & # Uptrend confirmation
                qtpylib.crossed_above(dataframe['close'], dataframe['vwap'])
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Sell when price crosses below VWAP
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe['close'], dataframe['vwap'])
            ),
            'exit_long'] = 1
        return dataframe
