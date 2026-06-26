<template>
  <div class="app-container">
    <aside class="sidebar">
      <h2>종목 리스트</h2>
      <div v-if="loadingList" class="loading">로딩 중...</div>
      <ul v-else>
        <li v-for="stock in allStocks" :key="stock.ticker" 
            :class="{ active: selectedTicker === stock.ticker }"
            @click="selectStock(stock.ticker)">
          <span class="ticker">{{ stock.ticker }}</span>
          <span class="name">{{ stock.name }}</span>
        </li>
      </ul>
    </aside>

    <main class="content">
      <div v-if="selectedTicker">
        <header class="header">
          <h1>{{ selectedTicker }} 분석 대시보드</h1>
        </header>

        <section class="metrics-container">
          <div v-for="m in stockMetrics" :key="m.label" class="metric-card">
            <span class="label">{{ m.label }}</span>
            <span class="value">{{ m.value }}</span>
          </div>
        </section>

        <section class="history-container">
          <h3>최근 거래 이력</h3>
          <div v-if="loadingDetail">데이터 로딩 중...</div>
          <table v-else>
            <thead>
              <tr>
                <th>날짜</th>
                <th>USD 가격</th>
                <th>KRW 가격</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in stockList" :key="item.date">
                <td>{{ item.date }}</td>
                <td class="usd">${{ item.usd_price.toLocaleString(undefined, {minimumFractionDigits:2}) }}</td>
                <td class="krw">₩{{ Math.floor(item.krw_price).toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </section>
      </div>

      <div v-else class="empty-state">
        <p>분석할 종목을 왼쪽에서 선택해 주세요.</p>
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
    const res = await axios.get('http://127.0.0.1:8000/stocks');
    allStocks.value = res.data;
  } finally { loadingList.value = false; }
};

const selectStock = async (ticker) => {
  selectedTicker.value = ticker;
  loadingDetail.value = true;
  try {
    const res = await axios.get(`http://127.0.0.1:8000/stocks/${ticker}`);
    stockMetrics.value = res.data.metrics; // 가치 정보 저장
    stockList.value = res.data.history;   // 이력 정보 저장
  } finally { loadingDetail.value = false; }
};

onMounted(fetchAllStocks);
</script>

<style scoped>
.app-container { display: flex; height: 100vh; font-family: sans-serif; background: #f4f7f6; }
.sidebar { width: 250px; background: #fff; border-right: 1px solid #ddd; padding: 20px; overflow-y: auto; }
.sidebar li { padding: 12px; cursor: pointer; border-radius: 6px; margin-bottom: 5px; border-bottom: 1px solid #eee; }
.sidebar li.active { background: #007bff; color: white; }

.content { flex: 1; padding: 40px; overflow-y: auto; }
.metrics-container { display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin-bottom: 30px; }
.metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
.metric-card .label { display: block; font-size: 0.8rem; color: #666; margin-bottom: 5px; }
.metric-card .value { font-size: 1.1rem; font-weight: bold; color: #007bff; }

.history-container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; border-bottom: 1px solid #eee; text-align: left; }
th { background: #f8f9fa; color: #333; }
.usd { font-weight: bold; }
.empty-state { display: flex; justify-content: center; align-items: center; height: 100%; color: #999; }
</style>