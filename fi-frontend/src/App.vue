<template>
  <el-container class="dashboard-wrapper" v-loading="loading" element-loading-text="데이터를 불러오는 중입니다...">
    
    <el-aside width="260px" class="sidebar">
      <div class="sidebar-header">
        <h2 class="brand">FI Analysis</h2>
      </div>
      
      <el-form class="filter-form" label-position="top">
        <el-divider content-position="left">종목 필터</el-divider>
        <el-form-item label="종목 검색">
          <el-input 
            v-model="searchQuery" 
            placeholder="티커 입력 후 버튼 클릭" 
            clearable 
            @keyup.enter="applyFilters"
          />
        </el-form-item>

        <el-divider content-position="left">가치투자 필터</el-divider>
        <el-form-item>
          <el-checkbox v-model="tempFilterBlueChip">우량주 (ROE > 15%)</el-checkbox>
          <el-checkbox v-model="tempFilterLowPer">저평가 (PER < 15)</el-checkbox>
        </el-form-item>
        
        <el-button type="primary" class="w-100" @click="applyFilters">데이터 적용 및 새로고침</el-button>
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
          <el-table :data="filteredStocks" stripe height="350" highlight-current-row @current-change="handleRowClick">
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
              <span>{{ selectedStock?.ticker || '종목' }} 주가 추이 (샘플)</span>
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

const stocks = ref([]);
const loading = ref(false);
const selectedStock = ref(null);
let chartInstance = null;

// [변경점 1] 입력창과 직접 연결된 "임시" 상태값들
const searchQuery = ref('');
const tempFilterBlueChip = ref(false);
const tempFilterLowPer = ref(false);

// [변경점 2] 실제 필터링에 사용될 "확정된" 상태값들
const finalSearchQuery = ref('');
const finalFilterBlueChip = ref(false);
const finalFilterLowPer = ref(false);

const API_URL = 'https://sj-fi.onrender.com/stocks';

// [변경점 3] filteredStocks는 이제 final... 값들만 바라봅니다.
const filteredStocks = computed(() => {
  return stocks.value.filter(s => {
    const nameMatch = s.ticker.toLowerCase().includes(finalSearchQuery.value.toLowerCase());
    const roeMatch = finalFilterBlueChip.value ? s.roe > 15 : true;
    const perMatch = finalFilterLowPer.value ? (s.per > 0 && s.per < 15) : true;
    return nameMatch && roeMatch && perMatch;
  });
});

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

// [변경점 4] 버튼을 눌렀을 때 실행되는 함수
const applyFilters = async () => {
  // 1. 임시 값을 확정 값으로 복사 (이때 테이블이 업데이트됨)
  finalSearchQuery.value = searchQuery.value;
  finalFilterBlueChip.value = tempFilterBlueChip.value;
  finalFilterLowPer.value = tempFilterLowPer.value;

  // 2. 백엔드에서 최신 데이터를 다시 가져옴
  await fetchStocks();
};

const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await axios.get(API_URL, { timeout: 60000 });
    stocks.value = response.data;
    if (stocks.value.length > 0) {
      // 필터링된 결과 중 첫 번째 선택
      await nextTick();
      if (filteredStocks.value.length > 0) {
        handleRowClick(filteredStocks.value[0]);
      }
    }
  } catch (error) {
    console.error("데이터 로드 실패:", error);
  } finally {
    loading.value = false;
  }
};

const handleRowClick = (row) => {
  if (row) {
    selectedStock.value = row;
    updateChart(row.ticker);
  }
};

const updateChart = (ticker) => {
  const ctx = document.getElementById('mainPriceChart')?.getContext('2d');
  if (!ctx) return;
  if (chartInstance) chartInstance.destroy();
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['12M', '9M', '6M', '3M', 'Now'],
      datasets: [{
        label: `${ticker} Price Trend`,
        data: Array.from({length: 5}, () => Math.floor(Math.random() * 50) + 150),
        borderColor: '#409eff',
        tension: 0.4
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
};

onMounted(fetchStocks);
</script>

<style scoped>
/* (기존 스타일과 동일) */
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