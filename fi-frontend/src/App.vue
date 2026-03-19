<template>
  <el-container class="dashboard-wrapper" v-loading="loading" element-loading-text="데이터를 불러오는 중입니다... (최대 1분 소요)">
    
    <el-aside width="260px" class="sidebar">
      <div class="sidebar-header">
        <h2 class="brand">FI Analysis</h2>
      </div>
      
      <el-form class="filter-form" label-position="top">
        <el-divider content-position="left">종목 필터</el-divider>
        <el-form-item label="종목 검색">
          <el-input v-model="searchQuery" placeholder="티커 입력 (예: AAPL)" clearable />
        </el-form-item>

        <el-divider content-position="left">가치투자 필터</el-divider>
        <el-form-item>
          <el-checkbox v-model="filterBlueChip">우량주 (ROE > 15%)</el-checkbox>
          <el-checkbox v-model="filterLowPer">저평가 (PER < 15)</el-checkbox>
        </el-form-item>
        
        <el-button type="primary" class="w-100" @click="fetchStocks">데이터 새로고침</el-button>
      </el-form>
    </el-aside>

    <el-container class="main-content">
      <el-header height="auto" class="stats-header">
        <el-row :gutter="20">
          <el-col :span="4" v-for="(val, label) in summaryStats" :key="label">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-label">{{ label }}</div>
              <div class="stat-value">{{ val || '-' }}</div>
            </el-card>
          </el-col>
        </el-row>
      </el-header>

      <el-main class="scroll-area">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>주식 데이터 리스트</span>
              <el-tag type="success">결과: {{ filteredStocks.length }}건</el-tag>
            </div>
          </template>
          <el-table 
            :data="filteredStocks" 
            stripe 
            height="350" 
            highlight-current-row
            @current-change="handleRowClick"
          >
            <el-table-column prop="ticker" label="티커" width="100" fixed sortable />
            <el-table-column prop="price" label="현재가" align="right" />
            <el-table-column prop="per" label="PER" align="right" sortable />
            <el-table-column prop="pbr" label="PBR" align="right" sortable />
            <el-table-column prop="roe" label="ROE (%)" align="right" sortable />
            <el-table-column prop="peg" label="PEG" align="right" sortable />
          </el-table>
        </el-card>

        <el-card class="section-card chart-container">
          <template #header>
            <div class="card-header">
              <span>{{ selectedStock?.ticker || '종목' }} 주가 추이 (샘플 데이터)</span>
            </div>
          </template>
          <div class="canvas-wrapper">
            <canvas id="mainPriceChart"></canvas>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import axios from 'axios';
import Chart from 'chart.js/auto';

// 상태 관리
const stocks = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const filterBlueChip = ref(false);
const filterLowPer = ref(false);
const selectedStock = ref(null);
let chartInstance = null;

// 백엔드 URL
const API_URL = 'https://sj-fi.onrender.com/stocks';

// 필터링 로직
const filteredStocks = computed(() => {
  return stocks.value.filter(s => {
    const nameMatch = s.ticker.toLowerCase().includes(searchQuery.value.toLowerCase());
    const roeMatch = filterBlueChip.value ? s.roe > 15 : true;
    const perMatch = filterLowPer.value ? (s.per > 0 && s.per < 15) : true;
    return nameMatch && roeMatch && perMatch;
  });
});

// 상단 지표 계산
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

// 데이터 가져오기 (응답 없음 방지 로직 포함)
const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await axios.get(API_URL, { timeout: 60000 }); // 60초까지 대기
    stocks.value = response.data;
    if (stocks.value.length > 0) {
      selectedStock.value = stocks.value[0];
      await nextTick(); // DOM 업데이트 대기
      updateChart(selectedStock.value.ticker);
    }
  } catch (error) {
    console.error("데이터 로드 실패:", error);
  } finally {
    loading.value = false;
  }
};

// 행 클릭 시 차트 및 지표 업데이트
const handleRowClick = (row) => {
  if (row) {
    selectedStock.value = row;
    updateChart(row.ticker);
  }
};

// 차트 생성 및 업데이트 함수
const updateChart = (ticker) => {
  const ctx = document.getElementById('mainPriceChart')?.getContext('2d');
  if (!ctx) return;

  if (chartInstance) {
    chartInstance.destroy(); // 메모리 누수 방지를 위해 기존 차트 파괴
  }

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['12M', '9M', '6M', '3M', 'Now'],
      datasets: [{
        label: `${ticker} Price Trend`,
        data: Array.from({length: 5}, () => Math.floor(Math.random() * 50) + 150),
        borderColor: '#409eff',
        backgroundColor: 'rgba(64, 158, 255, 0.1)',
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: true } }
    }
  });
};

onMounted(fetchStocks);
</script>

<style scoped>
.dashboard-wrapper { height: 100vh; background-color: #f5f7fa; display: flex; }
.sidebar { background: #fff; border-right: 1px solid #dcdfe6; padding: 20px; display: flex; flex-direction: column; }
.brand { color: #409eff; font-size: 1.5rem; margin-bottom: 30px; text-align: center; }

.main-content { display: flex; flex-direction: column; overflow: hidden; }
.stats-header { padding: 20px; background: #fff; border-bottom: 1px solid #dcdfe6; }
.stat-card { text-align: center; border: none; background: #f9fafc; }
.stat-label { font-size: 12px; color: #909399; margin-bottom: 5px; }
.stat-value { font-size: 18px; font-weight: bold; color: #303133; }

.scroll-area { padding: 20px; overflow-y: auto; }
.section-card { margin-bottom: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }

.chart-container { height: 400px; }
.canvas-wrapper { height: 300px; position: relative; }
.w-100 { width: 100%; }
</style>