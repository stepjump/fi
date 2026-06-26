<template>
  <div class="app-container">
    <aside class="sidebar">
      <h2>종목 리스트</h2>
      <div v-if="loadingList">로딩 중...</div>
      <ul v-else>
        <li
          v-for="stock in allStocks"
          :key="stock.ticker"
          :class="{ active: selectedTicker === stock.ticker }"
          @click="selectStock(stock.ticker)"
        >
          <span class="ticker">{{ stock.ticker }}</span>
          <span class="name">{{ stock.name }}</span>
        </li>
      </ul>
    </aside>

    <main class="content">
      <div v-if="selectedTicker">
        <header class="detail-header">
          <h1>{{ selectedTicker }} 종목 정보</h1>
        </header>

        <section class="summary-container">
          <div v-for="metric in stockMetrics" :key="metric.label" class="metric-card">
            <span class="label">{{ metric.label }}</span>
            <span class="value">{{ metric.value }}</span>
          </div>
        </section>

        <section class="history-container">
          <h3>최근 한 달 거래 이력</h3>
          <div v-if="loadingDetail">데이터 로딩 중...</div>
          <table v-else-if="stockList.length > 0">
            <thead>
              <tr>
                <th>날짜</th>
                <th>USD</th>
                <th>KRW</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in stockList" :key="item.date">
                <td>{{ item.date }}</td>
                <td>${{ item.usd_price.toLocaleString() }}</td>
                <td>₩{{ item.krw_price.toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </section>
      </div>

      <div v-else class="empty-state">
        <p>왼쪽 리스트에서 종목을 선택해 주세요.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const allStocks = ref([]);
const stockList = ref([]); // 한 달치 상세 데이터
const stockMetrics = ref([]); // 상단 5개 요약 정보
const selectedTicker = ref(null);
const loadingList = ref(false);
const loadingDetail = ref(false);

// 1. 전체 종목 리스트 가져오기
const fetchAllStocks = async () => {
  loadingList.value = true;
  try {
    const response = await axios.get('http://127.0.0.1:8000/stocks');
    allStocks.value = response.data;
  } catch (err) {
    console.error("종목 리스트 로드 실패", err);
  } finally {
    loadingList.value = false;
  }
};

// 2. 종목 선택 시 요약 정보 + 상세 리스트 가져오기
const selectStock = async (ticker) => {
  selectedTicker.value = ticker;
  loadingDetail.value = true;
  try {
    // 실제로는 API를 두 번 호출하거나, 하나의 엔드포인트에서 합쳐서 받아올 수 있습니다.
    const response = await axios.get(`http://127.0.0.1:8000/stocks/${ticker}`);
    
    // API 응답 구조에 따라 적절히 분리 (예시 데이터)
    stockList.value = response.data.history || response.data; 
    
    // 주요 가치 정보 5개 설정 (API에서 내려준다고 가정하거나 계산)
    // 예: 시가총액, PER, 배당수익률, 52주 최고가, 거래량
    stockMetrics.value = [
      { label: '시가총액', value: '1.2T' },
      { label: 'PER', value: '15.4' },
      { label: '배당수익률', value: '2.1%' },
      { label: '52주 최고', value: '$150.00' },
      { label: '거래량', value: '5.2M' }
    ];
  } catch (err) {
    console.error("데이터 로드 실패", err);
  } finally {
    loadingDetail.value = false;
  }
};

onMounted(fetchAllStocks);
</script>

<style scoped>
.app-container { display: flex; height: 100vh; font-family: 'Pretendard', sans-serif; color: #333; }

/* 사이드바 */
.sidebar { width: 260px; background: #fdfdfd; border-right: 1px solid #eee; padding: 20px; }
.sidebar li { padding: 15px; border-bottom: 1px solid #f0f0f0; cursor: pointer; transition: 0.2s; }
.sidebar li.active { background: #007bff; color: white; border-radius: 8px; }

/* 메인 콘텐츠 */
.content { flex: 1; padding: 30px; background: #f5f7f9; overflow-y: auto; }

/* 요약 카드 영역 */
.summary-container {
  display: grid;
  grid-template-columns: repeat(5, 1fr); /* 5칸 균등 배분 */
  gap: 15px;
  margin-bottom: 30px;
}
.metric-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  text-align: center;
}
.metric-card .label { font-size: 0.85rem; color: #777; margin-bottom: 8px; }
.metric-card .value { font-size: 1.1rem; font-weight: bold; color: #007bff; }

/* 테이블 영역 */
.history-container { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.history-container h3 { margin-top: 0; margin-bottom: 20px; font-size: 1.1rem; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; border-bottom: 1px solid #eee; text-align: left; }
th { color: #666; font-weight: 500; }
</style>