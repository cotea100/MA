
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from run_single_backtest import run_single_backtest
from run_ma_optimization import run_ma_optimization

st.set_page_config(page_title="MA Quant 전략 도구", layout="wide")
st.title("MA Quant - 이동평균 전략 백테스트 및 최적화")

# 탭 분리
mode = st.sidebar.radio("모드 선택", ["단일 전략 백테스트", "MA 기간 최적화"])

if mode == "단일 전략 백테스트":
    st.sidebar.subheader("단일 전략 설정")
    ticker = st.sidebar.text_input("종목 코드 (예: TSLA, 005930)", value="TSLA")
    market = st.sidebar.selectbox("시장 선택", ["US", "KR"])
    short_ma = st.sidebar.slider("단기 MA", 3, 60, 10)
    long_ma = st.sidebar.slider("장기 MA", 20, 200, 60)
    days = st.sidebar.number_input("백테스트 일수", min_value=100, max_value=1000, value=700)
    exclude = st.sidebar.number_input("최근 제외 일수", min_value=0, max_value=50, value=0)
    capital = st.sidebar.number_input("초기 자본금", value=1000 if market == "US" else 1000000)
    fee = st.sidebar.number_input("거래 수수료율", value=0.0025)

    if st.sidebar.button("백테스트 실행"):
        result_df, ori_df, summary = run_single_backtest(
            ticker, market, short_ma, long_ma, days, exclude, capital, fee
        )

        st.subheader("성과 요약")
        st.write(summary)

        st.subheader("누적 수익률")
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        ax1.plot(result_df.index, result_df['Cum_Ror'] * 100, label='전략')
        ax1.plot(ori_df.index, ori_df['OriCum_Ror'] * 100, label='단순 보유', linestyle='--')
        ax1.set_ylabel('%')
        ax1.set_title("누적 수익률 비교")
        ax1.legend()
        st.pyplot(fig1)

        st.subheader("드로우다운")
        fig2, ax2 = plt.subplots(figsize=(10, 3))
        ax2.plot(result_df.index, result_df['MaxDrawdown'] * 100, label='전략 MDD')
        ax2.plot(ori_df.index, ori_df['OriMaxDrawdown'] * 100, label='보유 MDD', linestyle='--')
        ax2.set_ylabel('%')
        ax2.legend()
        st.pyplot(fig2)

elif mode == "MA 기간 최적화":
    st.sidebar.subheader("최적화 설정")
    ticker = st.sidebar.text_input("종목 코드 (예: TSLA, 005930)", value="TSLA")
    market = st.sidebar.selectbox("시장 선택", ["US", "KR"])
    short_range = st.sidebar.slider("단기 MA 범위", 3, 60, (3, 20))
    long_range = st.sidebar.slider("장기 MA 범위", 20, 200, (20, 100))
    days = st.sidebar.number_input("데이터 수집 일수", min_value=100, max_value=1000, value=700)
    exclude = st.sidebar.number_input("최근 제외 일수", min_value=0, max_value=50, value=0)
    capital = st.sidebar.number_input("초기 자본금", value=1000 if market == "US" else 1000000)
    fee = st.sidebar.number_input("거래 수수료율", value=0.0025)

    if st.sidebar.button("최적화 실행"):
        result_df = run_ma_optimization(
            ticker, market, short_range, long_range, days, exclude, capital, fee
        )

        st.subheader("최적 MA 조합 결과")
        st.dataframe(result_df.sort_values(by="Score", ascending=True).head(10))

        csv = result_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="결과 CSV 다운로드",
            data=csv,
            file_name=f'{ticker}_ma_optimization_result.csv',
            mime='text/csv'
        )
