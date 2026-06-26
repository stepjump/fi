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
          <h1>{{ selectedTicker }} 이력</h1>
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
  const selectedTicker = ref(null);
  const loadingList = ref(false);
  const loadingDetail = ref(false);

  // 1. 페이지 로드 시 전체 종목 리스트 가져오기
  const fetchAllStocks = async () => {
    loadingList.value = true;
    try {
      const response = await axios.get('http://127.0.0.1:8000/stocks');
      allStocks.value = response.data;
    } catch (err) {
      console.error("종목 리스트를 가져오는데 실패했습니다.", err);
    } finally {
      loadingList.value = false;
    }
  };


// 2. 특정 종목 클릭 시 상세 데이터 가져오기
  const selectStock = async (ticker) => {
    selectedTicker.value = ticker;
    loadingDetail.value = true;
    try {
      const response = await axios.get(`http://127.0.0.1:8000/stocks/${ticker}`);
      stockList.value = response.data;
    } catch (err) {
      console.error("상세 데이터를 가져오는데 실패했습니다.", err);
    } finally {
      loadingDetail.value = false;
    }
  };


onMounted(fetchAllStocks);
  </script>

  <style scoped>
  .app-container { display: flex; height: 100vh; font-family: sans-serif; }

  /* 사이드바 스타일 */
  .sidebar { width: 250px; background: #f8f9fa; border-right: 1px solid #ddd; overflow-y: auto; padding: 20px; }
  .sidebar h2 { font-size: 1.2rem; margin-bottom: 20px; }
  .sidebar ul { list-style: none; padding: 0; }
  .sidebar li {
    padding: 12px; cursor: pointer; border-radius: 4px; margin-bottom: 5px;
    display: flex; flex-direction: column; transition: background 0.2s;
  }
  .sidebar li:hover { background: #e9ecef; }
  .sidebar li.active { background: #007bff; color: white; }
  .sidebar .ticker { font-weight: bold; }
  .sidebar .name { font-size: 0.85rem; opacity: 0.8; }


  /* 메인 콘텐츠 스타일 */
  .content { flex: 1; padding: 40px; overflow-y: auto; }
  .empty-state { display: flex; justify-content: center; align-items: center; height: 100%; color: #888; }
  table { width: 100%; border-collapse: collapse; margin-top: 20px; }
  th, td { border-bottom: 1px solid #eee; padding: 12px; text-align: left; }
  th { background: #f4f4f4; }
  </style>









