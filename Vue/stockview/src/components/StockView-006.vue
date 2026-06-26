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
          <h3>최근 거래 이력</h3>
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
                <td>${{ item.usd_price.toLocaleString(undefined, {minimumFractionDigits: 2}) }}</td>
                <td>₩{{ Math.floor(item.krw_price).toLocaleString() }}</td>
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
const stockList = ref([]); 
const stockMetrics = ref([]); 
const selectedTicker = ref(null);
const loadingList = ref(false);
const loadingDetail = ref(false);

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

const selectStock = async (ticker) => {
  selectedTicker.value = ticker;
  loadingDetail.value = true;
  try {
    // 백엔드 server.py의 수정된 엔드포인트 호출
    const response = await axios.get(`http://127.0.0.1:8000/stocks/${ticker}`);
    
    // 백엔드 응답 구조: { metrics: [...], history: [...] }
    stockMetrics.value = response.data.metrics; 
    stockList.value = response.data.history; 
    
  } catch (err) {
    console.error("상세 데이터 로드 실패", err);
    stockMetrics.value = [];
    stockList.value = [];
  } finally {
    loadingDetail.value = false;
  }
};

onMounted(fetchAllStocks);
</script>

<style scoped>
/* 기존 스타일 유지 */
.app-container { display: flex; height: 100vh; font-family: 'Pretendard', sans-serif; color: #333; }
.sidebar { width: 260px; background: #fdfdfd; border-right: 1px solid #eee; padding: 20px; overflow-y: auto; }
.sidebar h2 { font-size: 1.2rem; margin-bottom: 20px; }
.sidebar ul { list-style: none; padding: 0; }
.sidebar li { padding: 15px; border-bottom: 1px solid #f0f0f0; cursor: pointer; transition: 0.2s; display: flex; flex-direction: column; }
.sidebar li:hover { background: #f8f9fa; }
.sidebar li.active { background: #007bff; color: white; border-radius: 8px; }
.sidebar .ticker { font-weight: bold; }
.sidebar .name { font-size: 0.85rem; opacity: 0.9; }

.content { flex: 1; padding: 30px; background: #f5f7f9; overflow-y: auto; }
.detail-header { margin-bottom: 25px; }
.detail-header h1 { font-size: 1.5rem; margin: 0; }

.summary-container {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
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
.metric-card .label { font-size: 0.8rem; color: #777; margin-bottom: 8px; font-weight: 500; }
.metric-card .value { font-size: 1.05rem; font-weight: bold; color: #007bff; }

.history-container { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.history-container h3 { margin-top: 0; margin-bottom: 20px; font-size: 1.1rem; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; border-bottom: 1px solid #eee; text-align: left; }
th { background: #fafafa; color: #666; font-weight: 600; font-size: 0.9rem; }
.empty-state { display: flex; justify-content: center; align-items: center; height: 100%; color: #999; }
</style>