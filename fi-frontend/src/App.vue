<template>
  <el-container class="dashboard-container">
    <el-aside width="280px" class="sidebar">
      <div class="sidebar-logo">
        <h2 class="title">FI STOCK ANALYSIS</h2>
      </div>
      
      <el-form label-position="top" class="filter-section">
        <el-divider content-position="left">종목 검색</el-divider>
        <el-form-item>
          <el-input v-model="searchQuery" placeholder="티커 입력 (예: AAPL)" clearable />
        </el-form-item>

        <el-divider content-position="left">가치투자 필터</el-divider>
        <el-form-item>
          <el-checkbox v-model="filterBlueChip">우량주 (ROE > 15%)</el-checkbox>
          <el-checkbox v-model="filterLowPer">저평가 (PER < 15)</el-checkbox>
          <el-checkbox v-model="filterUnderValue">저PBR (PBR < 1.5)</el-checkbox>
        </el-form-item>
        
        <el-button type="primary" class="full-width" @click="fetchStocks">데이터 동기화</el-button>
      </el-form>
    </el-aside>

    <el-container class="main-layout">
      <el-header height="auto" class="value-header">
        <el-row :gutter="15">
          <el-col :span="4.8" v-for="(val, label) in summaryStats" :key="label">
            <el-card shadow="never" class="metric-card">
              <div class="metric-label">{{ label }}</div>
              <div class="metric-value">{{ val }}</div>
            </el-card>
          </el-col>
        </el-row>
      </el-header>

      <el-main class="content-area">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>주요 종목 데이터 리스트</span>
              <el-tag type="info">검색 결과: {{ filteredStocks.length }}건</el-tag>
            </div>
          </template>
          <el-table 
            :data="filteredStocks" 
            stripe 
            height="320" 
            style="width: 100%"
            highlight-current-row
            @current-change="handleRowClick"
          >
            <el-table-column prop="ticker" label="티커" width="100" fixed />
            <el-table-column prop="price" label="현재가" align="right" />
            <el-table-column prop="per" label="PER" align="right" sortable />
            <el-table-column prop="pbr" label="PBR" align="right" sortable />
            <el-table-column prop="roe" label="ROE (%)" align="right" sortable />
            <el-table-column prop="peg" label="PEG" align="right" sortable />
          </el-table>
        </el-card>

        <el-card class="section-card chart-section">
          <template #header>
            <div class="card-header">
              <span>{{ selectedStock?.ticker || '종목' }} 1년 주가 추이</span>
            </div>
          </template>
          <div class="canvas-wrapper">
            <canvas id="priceChart"></canvas>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import Chart from 'chart.js/auto';

// 상태 관리
const stocks = ref([]);
const searchQuery = ref('');
const filterBlueChip = ref(false);
const filterLowPer = ref(false);
const filterUnderValue = ref(false);
const selectedStock = ref(null);
let chartInstance = null;

// 백엔드 주소 (Render)
const API_URL = 'https://sj-fi.onrender.com/stocks';

// 필터링 로직
const filteredStocks = computed(() => {
  return stocks.value.filter(s => {
    const nameMatch = s.ticker.toLowerCase().includes(searchQuery.value.toLowerCase());
    const roeMatch = filterBlueChip.value ? s.roe > 15 : true;
    const perMatch = filterLowPer.value ? (s.per > 0 && s.per < 15) : true;
    const pbrMatch = filterUnderValue.value ? (s.pbr > 0 && s.pbr < 1.5) : true;
    return nameMatch && roeMatch && perMatch && pbrMatch;
  });
});

// 상단 요약 지표 계산
const summaryStats = computed(() => {
  const s = selectedStock.value;
  return {
    "현재가": s ? `$${s.price}` : '-',
    "PER": s ? s.per : '-',
    "PBR": s ? s.pbr : '-',
    "ROE": s ? `${s.roe}%` : '-',
    "PEG": s ? s.peg : '-'
  };
});

// 데이터 가져오기
const fetchStocks = async () => {
  try {
    const response = await axios.get(API_URL);
    stocks.value = response.data;
    if (stocks.value.length > 0) {
      selectedStock.value = stocks.value[0];
      initChart();
    }
  } catch (error) {
    console.error("데이터 로드 실패:", error);
  }
};

// 테이블 행 클릭 시 동작
const handleRowClick = (row) => {
  if (row) {
    selectedStock.value = row;
    updateChart(row.ticker);
  }
};

// 차트 초기화 및 업데이트
const initChart = () => {
  const ctx = document.getElementById('priceChart').getContext('2d');
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['12개월 전', '9개월 전', '6개월 전', '3개월 전', '현재'],
      datasets: [{
        label: '주가 추이',
        data: [100, 110, 105, 125, 120], // 실제 과거 데이터 API 연결 시 대체
        borderColor: '#409EFF',
        tension: 0.3,
        fill: true,
        backgroundColor: 'rgba(64, 158, 255, 0.1)'
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
};

const updateChart = (ticker) => {
  if (chartInstance) {
    // 임의의 데이터 변경 (나중에 백엔드 상세 데이터 API와 연결하세요)
    chartInstance.data.datasets[0].label = `${ticker} 주가`;
    chartInstance.data.datasets[0].data = Array.from({length: 5}, () => Math.floor(Math.random() * 100) + 100);
    chartInstance.update();
  }
};

onMounted(fetchStocks);
</script>

<style scoped>
.dashboard-container { height: 100vh; background-color: #f0f2f5; }
.sidebar { background-color: #fff; padding: 20px; border-right: 1px solid #e6e6e6; }
.sidebar-logo { text-align: center; margin-bottom: 30px; }
.title { font-size: 1.2rem; color: #409EFF; font-weight: bold; }
.full-width { width: 100%; margin-top: 20px; }

.main-layout { padding: 20px; }
.value-header { margin-bottom: 20px; background: transparent; padding: 0; }
.metric-card { text-align: center; border-radius: 8px; }
.metric-label { font-size: 0.85rem; color: #909399; margin-bottom: 8px; }
.metric-value { font-size: 1.2rem; font-weight: bold; color: #303133; }

.section-card { margin-bottom: 20px; border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; }

.chart-section { height: 350px; }
.canvas-wrapper { height: 280px; }
</style>