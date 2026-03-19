<template>
  <el-container class="dashboard-wrapper" v-loading="loading" element-loading-text="데이터를 불러오는 중입니다...">
    <el-aside width="260px" class="sidebar">
      <div class="sidebar-header"><h2 class="brand">FI Analysis</h2></div>
      <el-form class="filter-form" label-position="top">
        <el-divider content-position="left">종목 선택</el-divider>
        <el-form-item label="종목 리스트">
          <el-select v-model="tempSearchQuery" placeholder="종목 선택" clearable filterable class="w-100">
            <el-option v-for="item in uniqueStocks" :key="item.ticker" :label="`${item.ticker} (${item.name})`" :value="item.ticker" />
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
        <el-row :gutter="10">
          <el-col :span="3" v-for="(val, label) in summaryStats" :key="label">
            <el-card shadow="hover" class="stat-card">
              <div class="stat-label">{{ label }}</div>
              <div class="stat-value small-text">{{ val }}</div>
            </el-card>
          </el-col>
        </el-row>
      </el-header>

      <el-main class="scroll-area">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>전체 데이터 영역</span>
              <el-tag type="info">총 {{ filteredStocks.length }}건</el-tag>
            </div>
          </template>
          
          <el-table :data="filteredStocks" stripe height="400" highlight-current-row @current-change="handleRowClick" border style="width: 100%">
            <el-table-column prop="ticker" label="Ticker" width="90" fixed sortable />
            <el-table-column prop="name" label="Name" width="120" show-overflow-tooltip />
            <el-table-column prop="date" label="Date" width="100" sortable />
            
            <el-table-column prop="usd_price" label="USD Price" width="120" align="right">
              <template #default="scope">{{ formatDecimal(scope.row.usd_price) }}</template>
            </el-table-column>
            <el-table-column prop="krw_price" label="KRW Price" width="130" align="right">
              <template #default="scope">{{ formatDecimal(scope.row.krw_price) }}</template>
            </el-table-column>
            
            <el-table-column prop="close" label="Close" width="110" align="right">
              <template #default="scope">{{ formatDecimal(scope.row.close) }}</template>
            </el-table-column>
            <el-table-column prop="per" label="PER" width="80" align="right" sortable />
            <el-table-column prop="pbr" label="PBR" width="80" align="right" sortable />
            <el-table-column prop="psr" label="PSR" width="80" align="right" sortable />
            <el-table-column prop="pcr" label="PCR" width="80" align="right" sortable />
            <el-table-column prop="roe" label="ROE (%)" width="90" align="right" sortable />
            <el-table-column prop="eps" label="EPS" width="90" align="right" sortable />
            <el-table-column prop="peg" label="PEG" width="80" align="right" sortable />
            <el-table-column prop="dividend_yield" label="Div. Yield" width="110" align="right" sortable />
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

// 소수점 4자리 변환 함수
const formatDecimal = (val) => {
  const num = parseFloat(val);
  return isNaN(num) ? '0.0000' : num.toFixed(4);
};

// 데이터 유연 매핑 함수
const v = (obj, keys) => {
  for (const key of keys) {
    const val = obj[key] ?? obj[key.toUpperCase()] ?? obj[key.toLowerCase()];
    if (val !== undefined && val !== null) return val;
  }
  return 0;
};

const uniqueStocks = computed(() => {
  const map = new Map();
  if (!Array.isArray(allRawData.value)) return [];

  allRawData.value.forEach(item => {
    const tickerRaw = v(item, ['ticker', 'symbol', 'code']);
    if (!tickerRaw) return;
    
    const ticker = String(tickerRaw).trim().toUpperCase();
    
    map.set(ticker, {
      ticker: ticker,
      name: v(item, ['name', 'company_name']) || 'N/A',
      date: v(item, ['date', 'update_date']) || '-',
      usd_price: v(item, ['usd_price', 'price_usd']),
      krw_price: v(item, ['krw_price', 'price_krw']),
      close: v(item, ['close', 'closed_price']),
      per: v(item, ['per']),
      pbr: v(item, ['pbr']),
      psr: v(item, ['psr']),
      pcr: v(item, ['pcr']),
      roe: v(item, ['roe']),
      eps: v(item, ['eps']),
      peg: v(item, ['peg']),
      dividend_yield: v(item, ['dividend_yield', 'div_yield'])
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
    "Ticker": s ? s.ticker : '-',
    "USD Price": s ? formatDecimal(s.usd_price) : '-',
    "ROE": s ? `${s.roe}%` : '-',
    "PER": s ? s.per : '-',
    "PBR": s ? s.pbr : '-',
    "EPS": s ? s.eps : '-',
    "Div.Y": s ? `${s.dividend_yield}%` : '-'
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
    const data = Array.isArray(response.data) ? response.data : (response.data.stocks || []);
    allRawData.value = data;
    await nextTick();
    if (filteredStocks.value.length > 0) handleRowClick(filteredStocks.value[0]);
  } catch (error) {
    console.error("Fetch error:", error);
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
  if (!ctx || !ticker) return;
  if (chartInstance) chartInstance.destroy();
  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['12M', '9M', '6M', '3M', 'Now'],
      datasets: [{
        label: `${ticker} Trend`,
        data: Array.from({length: 5}, () => Math.floor(Math.random() * 50) + 100),
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
/* 이전 스타일 유지 */
.dashboard-wrapper { height: 100vh; background-color: #f5f7fa; display: flex; overflow: hidden; }
.sidebar { background: #fff; border-right: 1px solid #dcdfe6; padding: 20px; }
.brand { color: #409eff; font-size: 1.3rem; margin-bottom: 25px; text-align: center; font-weight: bold; }
.main-content { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.stats-header { padding: 15px; background: #fff; border-bottom: 1px solid #dcdfe6; }
.stat-card { text-align: center; background: #f9fafc; border: none; }
.stat-label { font-size: 11px; color: #909399; margin-bottom: 4px; }
.stat-value { font-size: 14px; font-weight: bold; color: #303133; white-space: nowrap; }
.small-text { font-size: 13px !important; }
.scroll-area { padding: 15px; overflow-y: auto; }
.section-card { margin-bottom: 15px; }
.chart-container { height: 300px; }
.canvas-wrapper { height: 240px; }
.w-100 { width: 100%; }
</style>