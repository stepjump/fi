<template>
  <div class="app-container">
    <aside class="sidebar">
      <h2>종목 리스트</h2>
      <div v-if="loadingList" class="loading-text">종목 불러오는 중...</div>
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
      <div v-if="selectedTicker" class="detail-layout">
        
        <section class="top-info">
          <div class="info-header">
            <h1>{{ selectedTicker }} <small>상세 정보</small></h1>
          </div>
          <div class="info-cards">
            <div class="card">
              <label>최근 달러가</label>
              <div class="val" v-if="stockList.length > 0">
                ${{ stockList[0].usd_price.toLocaleString() }}
              </div>
            </div>
            <div class="card highlight">
              <label>최근 원화가</label>
              <div class="val" v-if="stockList.length > 0">
                ₩{{ stockList[0].krw_price.toLocaleString() }}
              </div>
            </div>
          </div>
        </section>

        <section class="bottom-history">
          <h3>가격 변동 이력</h3>
          <div v-if="loadingDetail" class="loading-text">데이터 로딩 중...</div>
          <div v-else class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>날짜</th>
                  <th>USD (달러)</th>
                  <th>KRW (원화)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in stockList" :key="item.date">
                  <td class="date">{{ item.date }}</td>
                  <td class="usd">${{ item.usd_price.toLocaleString() }}</td>
                  <td class="krw">₩{{ item.krw_price.toLocaleString() }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

      </div>

      <div v-else class="empty-state">
        <div class="icon">📈</div>
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
const selectedTicker = ref(null);
const loadingList = ref(false);
const loadingDetail = ref(false);

// 1. 전체 종목 리스트 로드
const fetchAllStocks = async () => {
  loadingList.value = true;
  try {
    const response = await axios.get('http://127.0.0.1:8000/stocks');
    allStocks.value = response.data;
  } catch (err) {
    console.error("리스트 로드 실패", err);
  } finally {
    loadingList.value = false;
  }
};

// 2. 종목 선택 시 상세 이력 데이터 로드
const selectStock = async (ticker) => {
  selectedTicker.value = ticker;
  loadingDetail.value = true;
  try {
    const response = await axios.get(`http://127.0.0.1:8000/stocks/${ticker}`);
    stockList.value = response.data;
  } catch (err) {
    console.error("이력 로드 실패", err);
  } finally {
    loadingDetail.value = false;
  }
};

onMounted(fetchAllStocks);
</script>

<style scoped>
.app-container { display: flex; height: 100vh; font-family: 'Pretendard', sans-serif; background-color: #f0f2f5; }

/* 사이드바 */
.sidebar { width: 280px; background: #fff; border-right: 1px solid #dce0e5; padding: 20px; overflow-y: auto; }
.sidebar h2 { font-size: 1.1rem; color: #333; margin-bottom: 20px; }
.sidebar ul { list-style: none; padding: 0; }
.sidebar li {
  padding: 15px; cursor: pointer; border-radius: 10px; margin-bottom: 8px;
  display: flex; flex-direction: column; transition: 0.2s; border: 1px solid transparent;
}
.sidebar li:hover { background: #f8f9fa; border-color: #dee2e6; }
.sidebar li.active { background: #007bff; color: white; box-shadow: 0 4px 12px rgba(0,123,255,0.3); }
.sidebar .ticker { font-weight: 700; font-size: 1rem; }
.sidebar .name { font-size: 0.8rem; opacity: 0.8; margin-top: 4px; }

/* 메인 레이아웃 */
.content { flex: 1; padding: 30px; overflow-y: auto; }
.detail-layout { display: flex; flex-direction: column; gap: 25px; height: 100%; }

/* 상단 섹션 */
.top-info { background: #fff; padding: 20px; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.info-header h1 { font-size: 1.5rem; margin-bottom: 15px; }
.info-cards { display: flex; gap: 15px; }
.card { flex: 1; padding: 15px; background: #f8f9fa; border-radius: 10px; border-left: 4px solid #ced4da; }
.card.highlight { border-left-color: #007bff; }
.card label { font-size: 0.8rem; color: #6c757d; display: block; margin-bottom: 5px; }
.card .val { font-size: 1.3rem; font-weight: 800; color: #212529; }

/* 하단 섹션 */
.bottom-history { background: #fff; padding: 20px; border-radius: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); flex: 1; }
.bottom-history h3 { margin-bottom: 15px; font-size: 1.1rem; }
.table-wrapper { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 12px; background: #f8f9fa; color: #495057; font-weight: 600; border-bottom: 2px solid #dee2e6; }
td { padding: 12px; border-bottom: 1px solid #eee; }
.date { color: #868e96; }
.usd { color: #28a745; font-weight: 600; }
.krw { color: #dc3545; font-weight: 600; }

.empty-state { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; color: #adb5bd; }
.empty-state .icon { font-size: 4rem; margin-bottom: 10px; }
</style>