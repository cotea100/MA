
import pandas as pd
from KIS_Common import GetOhlcv

def run_single_backtest(ticker, market, short_ma, long_ma, days, exclude, capital, fee):
    df = GetOhlcv(market, ticker, days + exclude)
    df = df[:-exclude] if exclude > 0 else df
    df['short_ma'] = df['close'].rolling(short_ma).mean()
    df['long_ma'] = df['close'].rolling(long_ma).mean()
    df.dropna(inplace=True)

    invest = ori_invest = capital
    invest_list, ori_list = [], []
    buy = False
    buy_price = 0
    try_cnt = success = fail = 0

    for i in range(2, len(df)):
        now = df.iloc[i]['close']
        prev = df.iloc[i-1]['close']
        ori_invest *= (1 + (now - prev) / prev)

        if buy:
            invest *= (1 + (now - prev) / prev)
            if df.iloc[i-1]['short_ma'] < df.iloc[i-1]['long_ma'] and df.iloc[i-2]['short_ma'] > df.iloc[i-1]['short_ma']:
                rate = (now - buy_price) / buy_price
                invest *= (1 - fee)
                try_cnt += 1
                if rate > fee:
                    success += 1
                else:
                    fail += 1
                buy = False
        elif df.iloc[i-1]['short_ma'] > df.iloc[i-1]['long_ma'] and df.iloc[i-2]['short_ma'] < df.iloc[i-1]['short_ma']:
            buy_price = now
            invest *= (1 - fee)
            buy = True

        invest_list.append(invest)
        ori_list.append(ori_invest)

    result_df = pd.DataFrame({'Total_Money': invest_list}, index=df.index[-len(invest_list):])
    result_df['Ror'] = result_df['Total_Money'].pct_change() + 1
    result_df['Cum_Ror'] = result_df['Ror'].cumprod()
    result_df['Drawdown'] = result_df['Cum_Ror'] / result_df['Cum_Ror'].cummax() - 1
    result_df['MaxDrawdown'] = result_df['Drawdown'].cummin()

    ori_df = pd.DataFrame({'OriTotal_Money': ori_list}, index=result_df.index)
    ori_df['OriRor'] = ori_df['OriTotal_Money'].pct_change() + 1
    ori_df['OriCum_Ror'] = ori_df['OriRor'].cumprod()
    ori_df['OriDrawdown'] = ori_df['OriCum_Ror'] / ori_df['OriCum_Ror'].cummax() - 1
    ori_df['OriMaxDrawdown'] = ori_df['OriDrawdown'].cummin()

    years = (pd.to_datetime(df.index[-1]) - pd.to_datetime(df.index[len(df) - len(invest_list)])).days / 365.25
    cagr = ((invest / capital) ** (1 / years) - 1) * 100
    ori_cagr = ((ori_invest / capital) ** (1 / years) - 1) * 100

    summary = {
        '전략 수익률': f'{(invest / capital - 1) * 100:.2f}%',
        '전략 CAGR': f'{cagr:.2f}%',
        '전략 MDD': f'{result_df["MaxDrawdown"].min() * 100:.2f}%',
        '보유 수익률': f'{(ori_invest / capital - 1) * 100:.2f}%',
        '보유 CAGR': f'{ori_cagr:.2f}%',
        '보유 MDD': f'{ori_df["OriMaxDrawdown"].min() * 100:.2f}%',
        '매매 횟수': try_cnt,
        '성공/실패': f'{success}/{fail}'
    }

    return result_df, ori_df, summary
