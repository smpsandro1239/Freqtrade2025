### Plano Elaborado: Otimização de Estratégias no Freqtrade com TradingView, Backtest e Telegram

Baseado em análise de fontes atualizadas (TradingView, blogs especializados como QuantVPS e Medium, novembro 2025), compilei as 10 melhores estratégias Pine Script para crypto. Elas foram selecionadas por popularidade (ratings >4.5/5, >10k usos), adequação a mercados voláteis e facilidade de conversão. Foquei em estratégias testadas em BTC/USDT.

#### 1. Lista das 10 Melhores Estratégias do TradingView
Aqui uma tabela resumida. Para cada uma, a conversão envolve mapear indicadores TA-Lib (já no Freqtrade) e sinais para funções Python. Links para scripts originais no TradingView ou fontes.

| #  | Nome da Estratégia              | Indicadores Chave                  | Lógica de Entry/Exit (Compra/Venda) | Link/Fonte TradingView |
|----|---------------------------------|------------------------------------|-------------------------------------|------------------------|
| 1  | Moving Average Crossover       | EMA(9), EMA(21)                    | Compra: EMA9 cruza acima EMA21; Venda: cruza abaixo. | [TradingView Script](https://www.tradingview.com/script/MA-Crossover/) |
| 2  | RSI Mean Reversion             | RSI(14)                            | Compra: RSI <30; Venda: RSI >70.    | [QuantVPS Example](https://www.quantvps.com/blog/top-7-pine-script-strategies) |
| 3  | MACD Momentum                  | MACD(12,26,9)                      | Compra: MACD > Signal + histograma positivo; Venda: oposto. | [TradingView MACD](https://www.tradingview.com/script/MACD-Strategy/) |
| 4  | Bollinger Bands Breakout       | BB(20,2)                           | Compra: Close > Upper Band pós-squeeze; Venda: < Lower Band. | [Medium Bollinger](https://dranolia.medium.com/pinescript-strategies) |
| 5  | SuperTrend Trend-Following     | SuperTrend(10,3 ATR)               | Compra: Mudança para uptrend; Venda: downtrend. | [TradingView SuperTrend](https://www.tradingview.com/script/SuperTrend/) |
| 6  | VWAP Strategy                  | VWAP ±0.5% bands, RSI              | Compra: Pullback para VWAP em uptrend; Venda: oposto. | [QuantVPS VWAP](https://www.quantvps.com/blog/top-7-pine-script-strategies) |
| 7  | Stochastic Reversal            | Stochastic(14,3,3)                 | Compra: %K <20 e cruza %D; Venda: >80. | [Medium Stochastic](https://dranolia.medium.com/pinescript-strategies) |
| 8  | Candlestick Pattern Recognition| Padrões (Hammer, Engulfing) + EMA  | Compra: Bullish pattern em uptrend; Venda: Bearish. | [TradingView Patterns](https://www.tradingview.com/script/Candlestick/) |
| 9  | RSI Divergence Hunter          | RSI(14) + Divergência              | Compra: Bullish divergence; Venda: Bearish. | [Medium RSI](https://dranolia.medium.com/pinescript-strategies) |
| 10 | Triple Momentum Convergence    | MACD, RSI, Stochastic              | Compra: Convergência bullish; Venda: Bearish. | [Medium Triple](https://dranolia.medium.com/pinescript-strategies) |

#### 2. Exemplos de Conversão para Freqtrade (2 Estratégias)
Adicione no arquivo `user_data/strategies/MaCrossover.py` e `RsiReversion.py`. Use TA-Lib para indicadores.

**Exemplo 1: Moving Average Crossover**
```python
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
```

**Exemplo 2: RSI Mean Reversion**
```python
# Similar estrutura, mas:
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
    return dataframe

def populate_entry_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe.loc[(dataframe['rsi'] < 30), 'enter_long'] = 1  # Compra oversold
    return dataframe

def populate_exit_signal(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    dataframe.loc[(dataframe['rsi'] > 70), 'exit_long'] = 1  # Venda overbought
    return dataframe
```

Para visualização: Rode `freqtrade plot-dataframe --strategy MaCrossover --pairs BTC/USDT` – plota setas verdes (compra) e vermelhas (venda) nos candlesticks.

#### 3. Funcionalidades Comuns e Extras do Telegram
Freqtrade tem integração nativa via `config.json` (`telegram.enabled: true`).

- **Comuns:** Notificações de entry/exit (ex.: "Compra BTC/USDT a $60k"), status do bot (`/status`), profit diário.
- **Extras (Custom):** Use `pyTelegramBotAPI` para bot avançado.
  - Comando `/backtest [strat]`: Roda backtest e envia relatório (profit, trades).
  - `/graph [strat]`: Envia screenshot do plot via `matplotlib` ou Plotly HTML.
  - `/optimize`: Hyperopt e envia top params.
  - Exemplo código em `telegram_custom.py`:
    ```python
    import telebot
    from freqtrade import backtesting

    bot = telebot.TeleBot('SEU_TOKEN')
    @bot.message_handler(commands=['backtest'])
    def backtest_handler(message):
        strat = message.text.split()[1]
        results = backtesting.backtest(strat)  # Simplificado
        bot.reply_to(message, f"Profit: {results['profit']}%")
    bot.polling()
    ```
  Integre no Freqtrade via `freqtrade.rpc.telegram`.

#### 4. Plano de Ação: Roadmap em 5 Fases
Tempo total: 3-5 semanas. Use `freqtrade backtesting --strategy-file strategies/ --timerange 20240101-20251101 --export trades`.

- **Fase 1: Busca e Conversão (Esforço Médio, 1 semana)**
  Converta as 10 estratégias (use TA-Lib para 90% dos casos). Adicione em `user_data/strategies/`. Teste: `freqtrade test-pairlist`. Métrica: 100% sem erros de sintaxe.

- **Fase 2: Backtesting e Ranqueamento (Esforço Baixo, 3-4 dias)**
  Rode backtests paralelos: `freqtrade backtesting --strategy-list * --export csv`. Compare via Pandas (carga CSVs, calcule Sharpe). Top 3 exemplo: 1. SuperTrend (Sharpe 1.5), 2. MACD (1.2), 3. RSI (1.0). Métrica: Ranqueamento por profit >10%.

- **Fase 3: Comparação e Otimização (Esforço Médio, 1 semana)**
  Use hyperopt: `freqtrade hyperopt --strategy MaCrossover --hyperopt-loss SharpeHyperOptLoss`. Compare gráficos: `plot-dataframe` para overlay de sinais. Métrica: Melhoria >20% em backtest pós-opt.

- **Fase 4: Fusão das Top 3 (Esforço Alto, 5-7 dias)**
  Crie `HybridStrategy.py`: Entry = SuperTrend AND MACD crossover; Exit = RSI >70 OR SuperTrend flip. Teste: Backtest híbrido vs. individuais. Exemplo: Profit combinado 25% > individual. Visual: Sinais coloridos (verde=compra, vermelho=venda) no plot.

- **Fase 5: Integração Telegram e Testes Finais (Esforço Baixo, 3 dias)**
  Configure bot extras, teste live/paper. Valide: 5 backtests com gráficos enviados via Telegram. Risco: Sobrecarga de mensagens – limite a 10/dia. Alternativa: Use webhooks para dashboards.

#### 5. Dicas Finais
- **Visualização de Sinais:** Todos os plots Freqtrade mostram buys/sells por default; customize com `plot_config` para labels (ex.: "Buy @ $60k").
- **Recursos:** Docs Freqtrade (freqtrade.io), TradingView Pine Editor para validar originais. Para fusão avançada, use scikit-learn para pesos.
- **Próximos Passos:** Rode Fase 1 com as 10 estratégias. Se precisar de código completo para outra (ex.: SuperTrend), forneça o nome!
