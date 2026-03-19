<template>
  <el-container class="dashboard-wrapper" v-loading="loading" element-loading-text="데이터를 분석 중입니다...">
    <el-aside width="260px" class="sidebar">
      <div class="sidebar-header"><h2 class="brand">FI Analysis</h2></div>
      <el-form class="filter-form" label-position="top">
        <el-divider content-position="left">종목 선택</el-divider>
        <el-form-item label="종목 리스트">
          <el-select v-model="tempSearchQuery" placeholder="종목 선택" clearable filterable class="w-100">
            <el-option v-for="item in uniqueStocks" :key="item.ticker" :label="item.ticker" :value="item.ticker" />
          </el-select>
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
              <div class="stat-value">{{ val }}</div>
            </el-card>
          </el-col>
        </el-row>
      </el-header>

      <el-main class="scroll-area">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>주식 데이터 리스트</span>
              <el-tag :type="allRawData.length > 0 ? 'success' : 'danger'">
                수신 데이터: {{ allRawData.length }}건
              </el-tag>
            </div>
          </template>
          
          <el-table :data="filteredStocks" stripe height="350" highlight-current-row @current-change="handleRowClick" empty-text="데이터 구조를 확인 중이거나 결과가 없습니다.">
            <el-table-column prop="ticker" label="티커" width="100" fixed sortable />
            <el-table-column prop="price" label="현재가" align="right" />
            <el-table-column prop="per" label="PER" align="right" sortable />
            <el-table-column prop="pbr" label="PBR" align="right" sortable />
            <el-table-column prop="roe" label="ROE (%)" align="right" sortable />
            <el-table-column prop="peg" label="PEG" align="right" sortable />
          </el-table>
        </el-card>

        <el-card class="section-card chart-container">
          <div class="canvas-wrapper"><canvas id="mainPriceChart"></canvas></div>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import axios from 'axios';
import Chart from 'chart.js/auto';

const allRawData = ref([]); 
const loading = ref(false);
const selectedStock = ref(null);
let chartInstance = null;

const tempSearchQuery = ref('');
const tempFilterBlueChip = ref(false);
const tempFilterLowPer = ref(false);

const finalSearchQuery = ref('');
const finalFilterBlueChip = ref(false);
const finalFilterLowPer = ref(false);

const API_URL = 'https://sj-fi.onrender.com/stocks';

// 어떤 이름으로 데이터가 오든 찾아내는 매퍼 함수
const getValue = (obj, keys) => {
  for (const key of keys) {
    if (obj[key] !== undefined && obj[key] !== null) return obj[key];
  }
  return 0;
};

const uniqueStocks = computed(() => {
  const map = new Map();
  if (!Array.isArray(allRawData.value)) return [];

  allRawData.value.forEach(item => {
    // 티커 찾기 (ticker, Ticker, CODE, code 등)
    const tickerRaw = getValue(item, ['ticker', 'Ticker', 'code', 'CODE', 'symbol']);
    if (!tickerRaw) return;
    
    const ticker = String(tickerRaw).trim().toUpperCase();
    
    // 데이터 매핑 (백엔드 컬럼명에 맞춰 자동 탐색)
    map.set(ticker, {
      ticker: ticker,
      price: getValue(item, ['price', 'PRICE', 'current_price', '현재가']),
      per: getValue(item, ['per', 'PER', 'per_ratio']),
      pbr: getValue(item, ['pbr', 'PBR', 'pbr_ratio']),
      roe: getValue(item, ['roe', 'ROE', 'roe_ratio']),
      peg: getValue(item, ['peg', 'PEG', 'peg_ratio'])
    }); 
  });
  return Array.from(map.values()).sort((a, b) => a.ticker.localeCompare(b.ticker));
});

const filteredStocks = computed(() => {
  return uniqueStocks.value.filter(s => {
    const nameMatch = finalSearchQuery.value ? s.ticker === finalSearchQuery.value : true;
    const roeMatch = finalFilterBlueChip.value ? parseFloat(s.roe) >= 15 : true;
    const perMatch = finalFilterLowPer.value ? (parseFloat(s.per) > 0 && parseFloat(s.per) <= 15) : true;
    return nameMatch && roeMatch && perMatch;
  });
});

const summaryStats = computed(() => {
  const s = selectedStock.value;
  return {
    "현재가": s ? `${s.price}` : '-',
    "PER": s ? s.per : '-',
    "PBR": s ? s.pbr : '-',
    "ROE": s ? `${s.roe}%` : '-',
    "PEG": s ? s.peg : '-'
  };
});

const applyFilters = () => {
  finalSearchQuery.value = tempSearchQuery.value;
  finalFilterBlueChip.value = tempFilterBlueChip.value;
  finalFilterLowPer.value = tempFilterLowPer.value;
  fetchStocks();
};

const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await axios.get(API_URL);
    // 중요: 응답 데이터가 배열인지, 아니면 객체 안에 배열이 있는지 확인
    const data = Array.isArray(response.data) ? response.data : (response.data.stocks || response.data.data || []);
    allRawData.value = data;
    
    await nextTick();
    if (filteredStocks.value.length > 0) {
      handleRowClick(filteredStocks.value[0]);
    }
  } catch (error) {
    console.error("API 연결 실패:", error);
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
        label: `${ticker} Price`,
        data: Array.from({length: 5}, () => Math.floor(Math.random() * 50) + 100),
        borderColor: '#409eff',
        fill: true,
        backgroundColor: 'rgba(64, 158, 255, 0.1)'
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
};

onMounted(fetchStocks);
</script>

<style scoped>
.dashboard-wrapper { height: 100vh; background-color: #f5f7fa; display: flex; overflow: hidden; }
.sidebar { background: #fff; border-right: 1px solid #dcdfe6; padding: 20px; }
.brand { color: #409eff; font-size: 1.5rem; margin-bottom: 30px; text-align: center; }
.main-content { display: flex; flex-direction: column; flex: 1; }
.stats-header { padding: 20px; background: #fff; border-bottom: 1px solid #dcdfe6; }
.stat-card { text-align: center; background: #f9fafc; }
.stat-label { font-size: 12px; color: #909399; margin-bottom: 5px; }
.stat-value { font-size: 18px; font-weight: bold; color: #303133; }
.scroll-area { padding: 20px; overflow-y: auto; }
.section-card { margin-bottom: 20px; }
.chart-container { height: 350px; }
.canvas-wrapper { height: 280px; }
.w-100 { width: 100%; }
</style>