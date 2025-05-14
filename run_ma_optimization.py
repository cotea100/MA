
import pandas as pd
from KIS_Common import GetOhlcv

def run_ma_optimization(ticker, market, short_range, long_range, days, exclude, capital, fee):
    df = GetOhlcv(market, ticker, days + exclude)
    df = df[:-exclude] if exclude > 0 else df
    df.dropna(inplace=True)

    ma_dfs = [df['close'].rolling(i).mean().rename(f'{i}ma') for i in range(short_range[0], long_range[1] + 1)]
    df = pd.concat([df] + ma_dfs, axis=1).dropna()

    results = []
    for ma1 in range(short_range[0], short_range[1] + 1):
        for ma2 in range(long_range[0], long_range[1] + 1):
            if ma1 >= ma2: continue
            invest, buy = capital, False
            buy_price = 0
            inv_list = []

            for i in range(2, len(df)):
                now = df.iloc[i]['close']
                prev = df.iloc[i-1]['close']
                if buy:
                    invest *= (1 + (now - prev) / prev)
                    if df.iloc[i-1][f'{ma1}ma'] < df.iloc[i-1][f'{ma2}ma'] and df.iloc[i-2][f'{ma1}ma'] > df.iloc[i-1][f'{ma1}ma']:
                        invest *= (1 - fee)
                        buy = False
                elif df.iloc[i-1][f'{ma1}ma'] > df.iloc[i-1][f'{ma2}ma'] and df.iloc[i-2][f'{ma1}ma'] < df.iloc[i-1][f'{ma1}ma']:
                    buy_price = now
                    invest *= (1 - fee)
                    buy = True
                inv_list.append(invest)

            if inv_list:
                result_df = pd.DataFrame({'Total_Money': inv_list}, index=df.index[-len(inv_list):])
                result_df['Ror'] = result_df['Total_Money'].pct_change() + 1
                result_df['Cum_Ror'] = result_df['Ror'].cumprod()
                result_df['Drawdown'] = result_df['Cum_Ror'] / result_df['Cum_Ror'].cummax() - 1
                result_df['MaxDrawdown'] = result_df['Drawdown'].cummin()
                final = inv_list[-1]
                revenue = round((final / capital - 1) * 100, 2)
                mdd = round(result_df['MaxDrawdown'].min() * 100, 2)
                results.append({"ma_str": f"{ma1} {ma2}", "RevenueRate": revenue, "MDD": mdd})

    result_df = pd.DataFrame(results)
    result_df['RevenueRate_rank'] = result_df['RevenueRate'].rank(ascending=False)
    result_df['MDD_rank'] = result_df['MDD'].rank(ascending=True)
    result_df['Score'] = result_df['RevenueRate_rank'] + result_df['MDD_rank']
    return result_df.sort_values(by='Score')
