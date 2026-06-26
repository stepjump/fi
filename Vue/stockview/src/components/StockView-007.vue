<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>종목 리스트</h2>
      </div>
      <div v-if="loadingList" class="loading-text">종목 로딩 중...</div>
      <ul v-else class="stock-ul">
        <li
          v-for="stock in allStocks"
          :key="stock.ticker"
          :class="{ active: selectedTicker === stock.ticker }"
          @click="selectStock(stock.ticker)"
        >
          <span class="ticker-code">{{ stock.ticker }}</span>
          <span class="ticker-name">{{ stock.name }}</span>
        </li>
      </ul>
    </aside>

    <main class="content">
      <div v-if="selectedTicker" class="detail-view">
        <header class="content-header">
          <h1>{{ selectedTicker }} <span class="sub-title">실시간 종목 분석</span></h1>
        </header>

        <section class="metrics-grid">
          <div v-for="metric in stockMetrics" :key="metric.label" class="metric-card">
            <p class="metric-label">{{ metric.label }}</p>
            <p class="metric-value" :class="getMetricStatusClass(metric)">
              {{ metric.value }}
            </p>
          </div>
        </section>

        <section class="history-section">
          <div class="section-header">
            <h3>최근 거래 이력</h3>
            <span class="badge">최근 30일</span>
          </div>
          
          <div v-if="loadingDetail" class="loading-spinner">데이터를 불러오는 중...</div>
          <div v-else class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>거래 날짜</th>
                  <th>가격 (USD)</th>
                  <th>환산가 (KRW)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in stockList" :key="item.date">
                  <td>{{ item.date }}</td>
                  <td class="price-usd">${{ item.usd_price.toLocaleString(undefined, { minimumFractionDigits: 2 }) }}</td>
                  <td class="price-krw">₩{{ Math.floor(item.krw_price).toLocaleString() }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📈</div>
        <p>분석할 종목을 리스트에서 선택해 주세요.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// 상태 관리 변수
const allStocks = ref([]);
const stockList = ref([]);
const stockMetrics = ref([]);
const selectedTicker = ref(null);
const loadingList = ref(false);
const loadingDetail = ref(false);

// [함수] 1. 전체 종목 리스트 가져오기
const fetchAllStocks = async () => {
  loadingList.value = true;
  try {
    const response = await axios.get('http://127.0.0.1:8000/stocks');
    allStocks.value = response.data;
  } catch (err) {
    alert("서버 연결에 실패했습니다.");
  } finally {
    loadingList.value = false;
  }
};

// [함수] 2. 특정 종목 선택 및 데이터 로드
const selectStock = async (ticker) => {
  selectedTicker.value = ticker;
  loadingDetail.value = true;
  try {
    const response = await axios.get(`http://127.0.0.1:8000/stocks/${ticker}`);
    // 백엔드에서 정의한 구조대로 매핑
    stockMetrics.value = response.data.metrics; // 5개 지표
    stockList.value = response.data.history;    // 이력 데이터
  } catch (err) {
    console.error("데이터 로드 중 오류 발생", err);
  } finally {
    loadingDetail.value = false;
  }
};

// [함수] 지표 성격에 따른 색상 구분 (전일대비 등락)
const getMetricStatusClass = (metric) => {
  if (metric.label === '전일대비') {
    if (metric.value.includes('+')) return 'pos';
    if (metric.value.includes('-')) return 'neg';
  }
  return '';
};

onMounted(fetchAllStocks);
</script>

<style scoped>
/* 전체 레이아웃 */
.app-container { display: flex; height: 100vh; background-color: #f0f2f5; font-family: 'Pretendard', sans-serif; }

/* 사이드바 스타일 */
.sidebar { width: 280px; background: white; border-right: 1px solid #e1e4e8; display: flex; flex-direction: column; }
.sidebar-header { padding: 24px; border-bottom: 1px solid #f0f0f0; }
.sidebar-header h2 { margin: 0; font-size: 1.25rem; color: #1a1a1a; }
.stock-ul { list-style: none; padding: 10px; margin: 0; overflow-y: auto; }
.stock-ul li {
  padding: 16px; border-radius: 8px; cursor: pointer; margin-bottom: 4px;
  display: flex; flex-direction: column; transition: all 0.2s;
}
.stock-ul li:hover { background: #f5f7fa; }
.stock-ul li.active { background: #007bff; color: white; box-shadow: 0 4px 12px rgba(0,123,255,0.3); }
.ticker-code { font-weight: 700; font-size: 1.05rem; }
.ticker-name { font-size: 0.85rem; opacity: 0.8; margin-top: 4px; }

/* 메인 콘텐츠 스타일 */
.content { flex: 1; padding: 40px; overflow-y: auto; }
.content-header { margin-bottom: 30px; }
.content-header h1 { font-size: 1.8rem; margin: 0; display: flex; align-items: baseline; gap: 10px; }
.sub-title { font-size: 0.9rem; color: #888; font-weight: 400; }

/* 지표 카드 그리드 (5개 카드) */
.metrics-grid {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; margin-bottom: 40px;
}
.metric-card {
  background: white; padding: 24px; border-radius: 16px; 
  box-shadow: 0 2px 10px rgba(0,0,0,0.03); text-align: center;
}
.metric-label { font-size: 0.85rem; color: #666; margin-bottom: 12px; font-weight: 500; }
.metric-value { font-size: 1.3rem; font-weight: 800; color: #1a1a1a; }
.metric-value.pos { color: #d63031; } /* 상승 시 빨간색 */
.metric-value.neg { color: #0984e3; } /* 하락 시 파란색 */

/* 테이블 섹션 스타일 */
.history-section { background: white; border-radius: 16px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.badge { background: #eef2f7; color: #5a67d8; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.table-wrapper { border-radius: 8px; overflow: hidden; }
table { width: 100%; border-collapse: collapse; }
th { background: #f8f9fa; padding: 14px; text-align: left; font-size: 0.85rem; color: #777; border-bottom: 2px solid #f0f0f0; }
td { padding: 14px; border-bottom: 1px solid #f0f0f0; font-size: 0.95rem; }
.price-usd { font-weight: 600; color: #2d3436; }
.price-krw { color: #636e72; }

/* 기타 상태 표시 */
.empty-state {
  height: 80%; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #aaa;
}
.empty-icon { font-size: 4rem; margin-bottom: 20px; }
</style>