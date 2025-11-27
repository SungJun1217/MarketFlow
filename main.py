import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeoutError
import re

# 페이지 설정
st.set_page_config(
    page_title="MarketFlow",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일 (고급 디자인)
st.markdown("""
<style>
    /* 전역 스타일 */
    * {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* 메인 타이틀 스타일 - 애니메이션 그라데이션 */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s ease infinite;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* 메트릭 카드 스타일 - 글래스모피즘 */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1.1rem;
        font-weight: 700;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
    }
    
    /* 섹션 헤더 스타일 */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 1.2rem;
        border-radius: 16px;
        color: white;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3),
                    0 4px 16px rgba(118, 75, 162, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 10s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* 테이블 스타일 - 글래스모피즘 */
    .dataframe {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* 라이트 모드 스타일 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9ff 0%, #e8ecff 50%, #d6deff 100%);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05);
    }
    
    [data-testid="stExpander"] {
        border: 1px solid rgba(102, 126, 234, 0.2);
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08),
                    inset 0 1px 0 rgba(255, 255, 255, 0.5);
        transition: all 0.3s ease;
    }
    
    [data-testid="stExpander"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15),
                    inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }
    
    [data-testid="stMetricContainer"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 249, 255, 0.9) 100%);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15),
                    0 4px 16px rgba(118, 75, 162, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.5);
        border-left: 5px solid;
        border-image: linear-gradient(135deg, #667eea, #764ba2) 1;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stMetricContainer"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        opacity: 0.6;
    }
    
    [data-testid="stMetricContainer"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2),
                    0 6px 20px rgba(118, 75, 162, 0.15),
                    inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }
    
    /* 다크 모드 스타일 */
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
        }
        
        [data-testid="stExpander"] {
            border: 1px solid rgba(139, 154, 255, 0.3);
            background: rgba(30, 30, 46, 0.7);
            backdrop-filter: blur(10px);
        }
        
        [data-testid="stExpander"]:hover {
            box-shadow: 0 8px 30px rgba(139, 154, 255, 0.2),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        
        [data-testid="stMetricContainer"] {
            background: linear-gradient(135deg, rgba(30, 30, 46, 0.9) 0%, rgba(22, 33, 62, 0.9) 100%);
            border-image: linear-gradient(135deg, #8b9aff, #a78bfa) 1;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
                        0 4px 16px rgba(139, 154, 255, 0.1),
                        inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }
        
        [data-testid="stMetricContainer"]:hover {
            box-shadow: 0 12px 40px rgba(139, 154, 255, 0.25),
                        0 6px 20px rgba(167, 139, 250, 0.15),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        
        .stDataFrame {
            background: rgba(30, 30, 46, 0.6);
        }
    }
    
    /* 버튼 스타일 - 네온 효과 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 1.5rem;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4),
                    0 2px 10px rgba(118, 75, 162, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.5),
                    0 4px 15px rgba(118, 75, 162, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
        background-position: right center;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
    }
    
    /* 다크모드 버튼 */
    @media (prefers-color-scheme: dark) {
        .stButton > button {
            background: linear-gradient(135deg, #8b9aff 0%, #a78bfa 50%, #c084fc 100%);
            box-shadow: 0 4px 20px rgba(139, 154, 255, 0.5),
                        0 2px 10px rgba(167, 139, 250, 0.4),
                        inset 0 1px 0 rgba(255, 255, 255, 0.15);
        }
        
        .stButton > button:hover {
            box-shadow: 0 8px 30px rgba(139, 154, 255, 0.6),
                        0 4px 15px rgba(167, 139, 250, 0.5),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }
    }
    
    /* 텍스트 입력 스타일 */
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def fetch_single_stock(ticker, period="3mo", is_index=False, timeout=10):
    """단일 주식 데이터를 가져오는 함수 (장 시작 전/후 모두 지원) - 최적화 버전"""
    try:
        stock = yf.Ticker(ticker)
        
        # 병렬로 history와 info 가져오기 (더 빠름)
        # 지수는 짧은 기간만 필요
        hist_period = "5d" if is_index else period
        
        # 빠른 데이터 가져오기 - interval 최소화
        hist = stock.history(period=hist_period, timeout=timeout)
        
        # info 가져오기 (최적화)
        try:
            info = stock.info
        except:
            # info 가져오기 실패 시 빈 dict 사용
            info = {}
        
        # 히스토리에서 직접 가격 정보 추출 (더 빠름)
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            volume = hist['Volume'].iloc[-1] if len(hist) > 0 else 0
            
            # 전일 종가
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
            else:
                prev_close = current_price
        else:
            # 히스토리가 없으면 info에서 가져오기
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            prev_close = info.get('previousClose') or current_price
            volume = 0
        
        # 변동률 계산
        if prev_close and prev_close > 0:
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
        else:
            change = 0
            change_pct = 0
        
        # 이동평균선 계산 (지수는 제외, 최적화)
        ma20 = None
        ma60 = None
        ma20_status = "N/A"
        ma60_status = "N/A"
        
        if not is_index and not hist.empty:
            close_prices = hist['Close']
            hist_len = len(close_prices)
            
            if hist_len >= 60:
                # 벡터화된 계산으로 더 빠름
                ma20 = close_prices.tail(20).mean()
                ma60 = close_prices.tail(60).mean()
                
                if current_price > 0:
                    ma20_status = "상회" if current_price > ma20 else "하회"
                    ma60_status = "상회" if current_price > ma60 else "하회"
            elif hist_len >= 20:
                ma20 = close_prices.tail(20).mean()
                if current_price > 0:
                    ma20_status = "상회" if current_price > ma20 else "하회"
        
        # 시가총액 계산 (지수는 제외)
        market_cap = 0
        if not is_index:
            market_cap = info.get('marketCap', 0)
            if market_cap <= 0 and current_price > 0:
                shares_outstanding = info.get('sharesOutstanding', 0)
                if shares_outstanding > 0:
                    market_cap = shares_outstanding * current_price
        
        # info에서 안전하게 값 가져오기
        def safe_get(key, default='Unknown'):
            if isinstance(info, dict):
                return info.get(key, default)
            return getattr(info, key, default) if hasattr(info, key) else default
        
        return ticker, {
            'name': safe_get('longName', ticker),
            'price': current_price,
            'prev_close': prev_close,
            'change': change,
            'change_pct': change_pct,
            'volume': volume,
            'market_cap': market_cap,
            'sector': safe_get('sector', 'Unknown'),
            'industry': safe_get('industry', 'Unknown'),
            'ma20': ma20,
            'ma60': ma60,
            'ma20_status': ma20_status,
            'ma60_status': ma60_status
        }
    except Exception as e:
        # 오류 발생 시 None 반환
        return ticker, None

def get_stock_data_parallel(tickers, period="1d", max_workers=15, progress_callback=None, timeout=15):
    """주식 데이터를 병렬로 가져오는 함수 (진행 상황 추적 가능) - 최적화 버전"""
    data = {}
    total = len(tickers)
    completed = 0
    
    # 동적 워커 수 조정 (너무 많으면 오히려 느려질 수 있음)
    optimal_workers = min(max_workers, len(tickers), 32)
    
    # ThreadPoolExecutor를 사용하여 병렬 처리
    with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
        # 모든 티커에 대해 작업 제출
        future_to_ticker = {
            executor.submit(fetch_single_stock, ticker, period, False, timeout): ticker 
            for ticker in tickers
        }
        
        # 완료된 작업부터 처리 (타임아웃 처리)
        for future in as_completed(future_to_ticker, timeout=timeout * len(tickers)):
            try:
                ticker, result = future.result(timeout=timeout)
                completed += 1
                if result is not None:
                    data[ticker] = result
            except (FutureTimeoutError, Exception) as e:
                completed += 1
                # 타임아웃이나 오류 발생 시 해당 티커 스킵
                pass
            
            # 진행 상황 콜백 호출
            if progress_callback:
                progress_callback(completed, total)
    
    return data

# 캐시 설정 (진행 상황 없이 빠른 재사용)
@st.cache_data(ttl=10)  # 10초마다 캐시 갱신 (실시간 업데이트)
def get_stock_data_cached(tickers, period="3mo", max_workers=15):
    """주식 데이터를 병렬로 가져오는 함수 (캐시용) - 최적화"""
    # 티커 리스트를 정렬하여 캐시 효율성 향상
    sorted_tickers = tuple(sorted(tickers))
    return get_stock_data_parallel(sorted_tickers, period, max_workers, progress_callback=None, timeout=12)

@st.cache_data(ttl=10)
def get_index_data_cached(index_tickers_dict, max_workers=4):
    """주요 지수 데이터를 병렬로 가져오는 함수 (캐시용)"""
    index_data = {}
    index_list = list(index_tickers_dict.items())
    
    if not index_list:
        return index_data
    
    # 병렬로 지수 데이터 가져오기
    with ThreadPoolExecutor(max_workers=min(max_workers, len(index_list))) as executor:
        future_to_name = {
            executor.submit(fetch_single_stock, ticker, "5d", True, timeout=8): name
            for name, ticker in index_list
        }
        
        for future in as_completed(future_to_name, timeout=30):
            try:
                name = future_to_name[future]
                ticker, info = future.result(timeout=8)
                if info:
                    index_data[name] = info
            except (FutureTimeoutError, Exception):
                pass
    
    return index_data

def create_sector_tables(data):
    """섹터별로 그룹화된 테이블 생성"""
    # 섹터별로 데이터 그룹화
    sectors_data = {}
    for ticker, info in data.items():
        sector = info.get('sector', 'Unknown')
        if not sector or sector == 'None':
            sector = 'Unknown'
        
        if sector not in sectors_data:
            sectors_data[sector] = []
        
        sectors_data[sector].append({
            'ticker': ticker,
            'info': info
        })
    
    # 섹터별 테이블 생성 함수
    def create_styled_table(sector_data):
        # 종목 이름을 Yahoo Finance 링크로 변환
        table_data = []
        for item in sector_data:
            ticker = item['ticker']
            name = item['info']['name']
            yahoo_link = f"https://finance.yahoo.com/quote/{ticker}"
            # HTML 링크로 이름 생성
            linked_name = f'<a href="{yahoo_link}" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 600;">{name}</a>'
            
            table_data.append({
                '종목': ticker,
                '이름': linked_name,
                '산업': item['info'].get('industry', 'Unknown'),
                '현재가': f"${item['info']['price']:.2f}",
                '변동': f"${item['info']['change']:.2f}",
                '변동률 (%)': f"{item['info']['change_pct']:.2f}%",
                '20일선': item['info'].get('ma20_status', 'N/A'),
                '60일선': item['info'].get('ma60_status', 'N/A'),
                '거래량': f"{item['info']['volume']:,.0f}",
                '시가총액': f"${item['info']['market_cap']/1e9:.2f}B" if item['info']['market_cap'] > 0 else "N/A"
            })
        
        df = pd.DataFrame(table_data)
        
        # 변동률에 따라 색상 적용
        def color_change_pct(val):
            try:
                pct = float(val.replace('%', ''))
                if pct < 0:
                    return 'background-color: #ffebee; color: #c62828'
                elif pct > 0:
                    return 'background-color: #e8f5e9; color: #2e7d32'
                else:
                    return ''
            except:
                return ''
        
        # 변동 금액에 따라 색상 적용
        def color_change(val):
            try:
                change = float(val.replace('$', ''))
                if change < 0:
                    return 'background-color: #ffebee; color: #c62828'
                elif change > 0:
                    return 'background-color: #e8f5e9; color: #2e7d32'
                else:
                    return ''
            except:
                return ''
        
        # 이동평균선 상태에 따라 색상 적용
        def color_ma_status(val):
            if val == "상회":
                return 'background-color: #e8f5e9; color: #2e7d32; font-weight: bold'
            elif val == "하회":
                return 'background-color: #ffebee; color: #c62828; font-weight: bold'
            else:
                return ''
        
        # 스타일 적용
        styled_df = df.style.map(
            color_change_pct,
            subset=['변동률 (%)']
        ).map(
            color_change,
            subset=['변동']
        ).map(
            color_ma_status,
            subset=['20일선', '60일선']
        ).set_table_styles([
            {'selector': 'th', 'props': [('font-size', '14px'), ('padding', '12px')]},
            {'selector': 'td', 'props': [('font-size', '13px'), ('padding', '10px 12px')]},
        ])
        
        return styled_df
    
    return sectors_data, create_styled_table

# 메인 앱
def main():
    # 헤더 섹션 - 고급 디자인
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0 2rem 0; position: relative;">
        <div style="position: absolute; top: 0; left: 50%; transform: translateX(-50%); 
                    width: 300px; height: 300px; background: radial-gradient(circle, 
                    rgba(102, 126, 234, 0.15) 0%, transparent 70%); border-radius: 50%; 
                    filter: blur(60px); z-index: -1; animation: pulse 3s ease-in-out infinite;"></div>
        <h1 style="font-size: 3.8rem; font-weight: 800; 
                   background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                   background-size: 200% 200%;
                   -webkit-background-clip: text; 
                   -webkit-text-fill-color: transparent; 
                   margin-bottom: 1rem;
                   letter-spacing: -2px;
                   animation: gradientShift 4s ease infinite;
                   text-shadow: 0 0 40px rgba(102, 126, 234, 0.2);">
        📊 실시간 주식 시장 대시보드
        </h1>
        <p style="font-size: 1.4rem; color: var(--text-color-secondary, #666); 
                  margin-top: 0.5rem; font-weight: 500; opacity: 0.9;
                  letter-spacing: 0.5px;">
        ✨ 실시간 주식 데이터를 섹터별로 확인하세요
        </p>
    </div>
    <style>
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.5; transform: translateX(-50%) scale(1); }
            50% { opacity: 0.8; transform: translateX(-50%) scale(1.1); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 사이드바 설정
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="font-size: 1.8rem; font-weight: 700; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            ⚙️ 설정
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # 기본 종목 리스트 (주요 미국 주식 - S&P 500 대표 종목)
        default_tickers = [
            # Technology
            'AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL', 'ADBE', 'CRM', 'AMD', 'INTC', 'QCOM',
            # Communication Services
            'GOOGL', 'GOOG', 'META', 'NFLX', 'DIS',
            # Consumer Cyclical
            'AMZN', 'TSLA', 'HD', 'NKE', 'SBUX', 'MCD',
            # Consumer Defensive
            'WMT', 'PG', 'KO', 'PEP', 'COST',
            # Healthcare
            'JNJ', 'UNH', 'LLY', 'MRK', 'ABBV', 'TMO', 'ABT', 'DHR',
            # Financial
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA', 'AXP', 'BRK-B',
            # Industrial
            'BA', 'CAT', 'GE', 'HON', 'UPS',
            # Energy
            'XOM', 'CVX', 'SLB', 'COP',
            # Real Estate
            'AMT', 'PLD', 'EQIX',
            # Utilities
            'NEE', 'DUK', 'SO',
            # Materials
            'LIN', 'APD', 'ECL'
        ]
        
        st.markdown("### 📝 종목 코드 입력")
        ticker_input = st.text_area(
            "종목 코드를 쉼표로 구분하여 입력하세요",
            value=", ".join(default_tickers),
            height=150,
            help="여러 종목을 추적하려면 쉼표로 구분하여 입력하세요"
        )
        
        tickers = [t.strip().upper() for t in ticker_input.split(',') if t.strip()]
        
        st.markdown("---")
        st.markdown("### 🔄 데이터 업데이트")
        
        # 수동 새로고침 버튼 (주요 기능)
        if st.button("🔄 데이터 새로고침", type="primary", key="manual_refresh", width='content'):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div style="padding: 1rem; background: rgba(240, 240, 240, 0.3); 
                    border-radius: 8px; font-size: 0.85rem; 
                    border: 1px solid rgba(128, 128, 128, 0.2); opacity: 0.9;">
            💡 <strong>팁:</strong> 최신 데이터를 보려면 '데이터 새로고침' 버튼을 클릭하세요.
        </div>
        """, unsafe_allow_html=True)
    
    if not tickers:
        st.warning("종목 코드를 입력해주세요.")
        return
    
    # 데이터 로딩 (병렬 처리로 빠르게)
    # 세션 상태를 사용하여 새로고침 여부 확인
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    # 주요 지수 티커 정의
    index_tickers = {
        'S&P 500': '^GSPC',
        '나스닥': '^IXIC',
        '다우존스': '^DJI',
        '러셀 2000': '^RUT'
    }
    
    # 주식 데이터와 지수 데이터를 병렬로 가져오기 (더 빠름)
    with st.spinner("주식 및 지수 데이터를 가져오는 중..."):
        # 병렬로 두 작업 실행
        with ThreadPoolExecutor(max_workers=2) as executor:
            # 이동평균 계산을 위해 최소 3개월 데이터 필요하지만, 더 빠른 로딩을 위해 2개월로 조정 가능
            # 60일 이동평균을 위해 최소 3개월 필요
            stock_future = executor.submit(get_stock_data_cached, tickers, "3mo", 32)
            index_future = executor.submit(get_index_data_cached, index_tickers, 4)
            
            # 결과 가져오기
            data = stock_future.result()
            index_data = index_future.result()
    
    if not data:
        st.error("데이터를 가져올 수 없습니다. 종목 코드를 확인해주세요.")
        return
    
    # 장 상태 확인 (변동률이 모두 0에 가까우면 장 시작 전으로 간주)
    all_changes_zero = all(abs(info.get('change_pct', 0)) < 0.01 for info in data.values())
    market_status = "⏸️ 장 시작 전" if all_changes_zero else "🟢 장 진행 중"
    
    # 장 상태 배너 (다크모드 대응)
    if all_changes_zero:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1rem; border-radius: 10px; color: white; 
                    text-align: center; font-size: 1.1rem; font-weight: 600; margin-bottom: 2rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);">
            {market_status} | 전일 종가 기준으로 표시됩니다
        </div>
        """.format(market_status=market_status), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1rem; border-radius: 10px; color: white; 
                    text-align: center; font-size: 1.1rem; font-weight: 600; margin-bottom: 2rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);">
            {market_status} | 실시간 데이터 업데이트 중
        </div>
        """.format(market_status=market_status), unsafe_allow_html=True)
    
    # 메트릭 표시 - 고급 디자인
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
                padding: 1.5rem; border-radius: 20px; color: white; 
                font-size: 1.8rem; font-weight: 700; margin: 2rem 0 1.5rem 0; 
                text-align: center; position: relative; overflow: hidden;
                box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3),
                            0 4px 16px rgba(118, 75, 162, 0.2);">
        <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%;
                    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                    animation: rotate 10s linear infinite;"></div>
        <span style="position: relative; z-index: 1;">📈 주요 지표</span>
    </div>
    <style>
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 주요 지수 표시
    if index_data:
        st.markdown("### 📊 주요 지수")
        index_cols = st.columns(4)
        index_names = ['S&P 500', '나스닥', '다우존스', '러셀 2000']
        
        for idx, index_name in enumerate(index_names):
            if index_name in index_data:
                info = index_data[index_name]
                price = info.get('price', 0)
                change_pct = info.get('change_pct', 0)
                
                with index_cols[idx]:
                    # 가격 포맷팅 (지수는 소수점 없이 표시)
                    if price > 0:
                        if price > 10000:
                            price_str = f"{price:,.0f}"
                        else:
                            price_str = f"{price:,.2f}"
                    else:
                        price_str = "N/A"
                    
                    st.metric(
                        index_name,
                        price_str,
                        delta=f"{change_pct:+.2f}%",
                        delta_color="normal" if change_pct >= 0 else "inverse"
                    )
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # 종목 통계
    st.markdown("### 📊 종목 통계")
    col1, col2, col3, col4 = st.columns(4)
    
    total_stocks = len(data)
    up_stocks = sum(1 for info in data.values() if info.get('change_pct', 0) > 0.01)
    down_stocks = sum(1 for info in data.values() if info.get('change_pct', 0) < -0.01)
    avg_change = sum(info.get('change_pct', 0) for info in data.values()) / total_stocks if total_stocks > 0 else 0
    
    with col1:
        st.metric(
            "📊 총 종목 수", 
            total_stocks,
            help="현재 추적 중인 종목 수"
        )
    with col2:
        st.metric(
            "📈 상승 종목", 
            up_stocks, 
            delta=f"{up_stocks/total_stocks*100:.1f}%" if total_stocks > 0 else "0%",
            delta_color="normal",
            help="상승 중인 종목 수"
        )
    with col3:
        st.metric(
            "📉 하락 종목", 
            down_stocks, 
            delta=f"{down_stocks/total_stocks*100:.1f}%" if total_stocks > 0 else "0%",
            delta_color="inverse",
            help="하락 중인 종목 수"
        )
    with col4:
        st.metric(
            "📊 평균 변동률", 
            f"{avg_change:.2f}%",
            help="전체 종목의 평균 변동률"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 섹터별 상세 테이블 - 고급 디자인
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%); 
                padding: 1.5rem; border-radius: 20px; color: white; 
                font-size: 1.8rem; font-weight: 700; margin: 2rem 0 1.5rem 0; 
                text-align: center; position: relative; overflow: hidden;
                box-shadow: 0 8px 32px rgba(240, 147, 251, 0.3),
                            0 4px 16px rgba(245, 87, 108, 0.2);">
        <div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
                    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                    animation: rotate 10s linear infinite;"></div>
        <span style="position: relative; z-index: 1;">📋 섹터별 상세 정보</span>
    </div>
    """, unsafe_allow_html=True)
    
    sectors_data, create_styled_table = create_sector_tables(data)
    
    # 섹터별로 정렬 (종목 수가 많은 순서대로)
    sorted_sectors = sorted(sectors_data.items(), key=lambda x: len(x[1]), reverse=True)
    
    for sector, sector_data in sorted_sectors:
        # 섹터별 헤더
        sector_count = len(sector_data)
        sector_avg_change = sum(item['info'].get('change_pct', 0) for item in sector_data) / sector_count if sector_count > 0 else 0
        sector_up = sum(1 for item in sector_data if item['info'].get('change_pct', 0) > 0.01)
        sector_down = sum(1 for item in sector_data if item['info'].get('change_pct', 0) < -0.01)
        
        # 섹터 헤더 스타일링 - 고급 디자인
        sector_color = "#4facfe" if sector_avg_change >= 0 else "#f5576c"
        sector_color2 = "#00f2fe" if sector_avg_change >= 0 else "#f093fb"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {sector_color} 0%, {sector_color2} 50%, #667eea 100%); 
                    padding: 1.2rem; border-radius: 16px; color: white; 
                    font-size: 1.3rem; font-weight: 700; margin: 1.5rem 0 1rem 0;
                    position: relative; overflow: hidden;
                    box-shadow: 0 6px 24px rgba(79, 172, 254, 0.3),
                                0 3px 12px rgba(102, 126, 234, 0.2);
                    transition: all 0.3s ease;">
            <div style="position: absolute; top: -50%; right: -50%; width: 200%; height: 200%;
                        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
                        animation: rotate 8s linear infinite;"></div>
            <span style="position: relative; z-index: 1;">
                🏢 {sector} | {sector_count}개 종목 | 평균: {sector_avg_change:+.2f}% | 📈 {sector_up} | 📉 {sector_down}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # 섹터 헤더
        with st.expander(f"📊 {sector} 상세 정보 보기", expanded=True):
            # 섹터 내 종목을 시가총액 기준 내림차순으로 정렬
            sorted_sector_data = sorted(sector_data, key=lambda x: x['info'].get('market_cap', 0), reverse=True)
            
            styled_table = create_styled_table(sorted_sector_data)
            # HTML로 렌더링하여 링크가 작동하도록 함
            table_id = f"table_{hash(sector) % 10000}"  # 고유 ID 생성
            html_table = styled_table.to_html(escape=False, index=False, table_id=table_id)
            
            # pandas가 생성한 스타일 태그를 추출하고 정리
            style_match = re.search(r'<style type="text/css">(.*?)</style>', html_table, re.DOTALL)
            pandas_styles = ""
            if style_match:
                # 스타일 내용 추출
                pandas_styles = style_match.group(1).strip()
                # HTML에서 스타일 태그 제거
                html_table = re.sub(r'<style type="text/css">.*?</style>', '', html_table, flags=re.DOTALL)
            
            # 스타일을 추가하여 테이블이 더 예쁘게 보이도록
            styled_html = f"""
            <style>
                /* pandas 스타일 (셀별 색상) */
                {pandas_styles}
                
                /* 커스텀 테이블 스타일 */
                #{table_id} {{
                    width: 100%;
                    border-collapse: collapse;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                    margin: 1rem 0;
                }}
                #{table_id} th {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                }}
                #{table_id} td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
                }}
                #{table_id} tr:hover {{
                    background-color: rgba(102, 126, 234, 0.05);
                }}
                #{table_id} a {{
                    color: #667eea;
                    text-decoration: none;
                    font-weight: 600;
                    transition: all 0.2s ease;
                }}
                #{table_id} a:hover {{
                    color: #764ba2;
                    text-decoration: underline;
                }}
            </style>
            {html_table}
            """
            st.markdown(styled_html, unsafe_allow_html=True)
    
    # 업데이트 시간 표시 (다크모드 대응)
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; 
                background: rgba(245, 245, 245, 0.3); 
                border-radius: 10px; margin-top: 2rem; 
                border: 1px solid rgba(128, 128, 128, 0.2);">
        <p style="font-size: 0.9rem; margin: 0; opacity: 0.8;">
            🔄 마지막 업데이트: <strong>{update_time}</strong> | 
            사이드바의 '데이터 새로고침' 버튼을 클릭하여 최신 데이터를 가져오세요
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

