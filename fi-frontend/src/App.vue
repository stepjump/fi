<template>
  <el-container class="dashboard-wrapper" v-loading="loading" element-loading-text="데이터를 불러오는 중입니다...">
    <el-aside width="280px" class="sidebar">
      <div class="sidebar-header"><h2 class="brand">FI Analysis</h2></div>
      
      <el-form class="filter-form" label-position="top">
        <el-divider content-position="left">조회 기간</el-divider>
        <el-form-item label="시작일자">
          <el-date-picker
            v-model="startDate"
            type="date"
            placeholder="시작일 선택"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="w-100"
          />
        </el-form-item>
        <el-form-item label="종료일자">
          <el-date-picker
            v-model="endDate"
            type="date"
            placeholder="종료일 선택"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="w-100"
          />
        </el-form-item>

        <el-divider content-position="left">종목 선택</el-divider>
        <el-form-item label="특정 종목 필터">
          <el-select v-model="tempSearchQuery" placeholder="전체 보기" clearable filterable class="w-100">
            <el-option v-for="item in tickerList" :key="item" :label="item" :value="item" />
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
      <el-main class="scroll-area">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span class="title-text">전체 데이터 영역 (기간별 상세)</span>
              <div>
                <el-tag type="info" effect="plain" class="mx-1">조회 범위: {{ finalStartDate || '전체' }} ~ {{ finalEndDate || '현재' }}</el-tag>
                <el-tag type="success">총 {{ filteredStocks.length }}건</el-tag>
              </div>
            </div>
          </template>
          
          <el-table :data="filteredStocks" stripe height="550" highlight-current-row @current-change="handleRowClick" border style="width: 100%">
            <el-table-column prop="ticker" label="Ticker" width="90" fixed sortable />
            <el-table-column prop="name" label="Name" width="120" show-overflow-tooltip />
            <el-table-column prop="date" label="Date" width="110" sortable />
            <el-table-column prop="usd_price" label="USD Price" width="110" align="right">
              <template #default="scope">{{ formatDecimal(scope.row.usd_price) }}</template>
            </el-table-column>
            <el-table-column prop="krw_price" label="KRW Price" width="120" align="right">
              <template #default="scope">{{ formatDecimal(scope.row.krw_price) }}</template>
            </el-table-column>
            <el-table-column prop="close" label="Close" width="100" align="right">
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

// 필터 상태값들
const startDate = ref('');
const endDate = ref('');
const tempSearchQuery = ref('');
const tempFilterBlueChip = ref(false);
const tempFilterLowPer = ref(false);

const finalStartDate = ref('');
const finalEndDate = ref('');
const finalSearchQuery = ref('');
const finalFilterBlueChip = ref(false);
const finalFilterLowPer = ref(false);

const API_URL = 'https://sj-fi.onrender.com/stocks';

const formatDecimal = (val) => {
  const num = parseFloat(val);
  return isNaN(num) ? '0.0000' : num.toFixed(4);
};

const v = (obj, keys) => {
  for (const key of keys) {
    const val = obj[key] ?? obj[key.toUpperCase()] ?? obj[key.toLowerCase()];
    if (val !== undefined && val !== null) return val;
  }
  return 0;
};

// 콤보박스용 유니크 티커 리스트
const tickerList = computed(() => {
  const set = new Set();
  allRawData.value.forEach(item => {
    const t = v(item, ['ticker', 'symbol', 'code']);
    if (t) set.add(String(t).trim().toUpperCase());
  });
  return Array.from(set).sort();
});

// 기간 및 조건 필터링 로직 (중복 제거 없이 전체 이력 출력)
const filteredStocks = computed(() => {
  let data = allRawData.value.map(item => ({
    ticker: String(v(item, ['ticker', 'symbol'])).trim().toUpperCase(),
    name: v(item, ['name', 'company_name']) || 'N/A',
    date: v(item, ['date', 'update_date']) || '-',
    usd_price: v(item, ['usd_price']),
    krw_price: v(item, ['krw_price']),
    close: v(item, ['close']),
    per: v(item, ['per']),
    pbr: v(item, ['pbr']),
    psr: v(item, ['psr']),
    pcr: v(item, ['pcr']),
    roe: v(item, ['roe']),
    eps: v(item, ['eps']),
    peg: v(item, ['peg']),
    dividend_yield: v(item, ['dividend_yield'])
  }));

  return data.filter(s => {
    // 1. 기간 필터
    const itemDate = s.date;
    const dateMatch = (!finalStartDate.value || itemDate >= finalStartDate.value) &&
                      (!finalEndDate.value || itemDate <= finalEndDate.value);
    
    // 2. 종목 필터
    const tickerMatch = finalSearchQuery.value ? s.ticker === finalSearchQuery.value : true;
    
    // 3. 지표 필터
    const roeMatch = finalFilterBlueChip.value ? parseFloat(s.roe) >= 15 : true;
    const perMatch = finalFilterLowPer.value ? (parseFloat(s.per) > 0 && parseFloat(s.per) <= 15) : true;

    return dateMatch && tickerMatch && roeMatch && perMatch;
  }).sort((a, b) => b.date.localeCompare(a.date)); // 최신 날짜순 정렬
});

const applyFilters = () => {
  finalStartDate.value = startDate.value;
  finalEndDate.value = endDate.value;
  finalSearchQuery.value = tempSearchQuery.value;
  finalFilterBlueChip.value = tempFilterBlueChip.value;
  finalFilterLowPer.value = tempFilterLowPer.value;
  fetchStocks();
};

const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await axios.get(API_URL);
    allRawData.value = Array.isArray(response.data) ? response.data : (response.data.stocks || []);
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

  // 차트 데이터도 해당 기간/종목의 데이터를 추출하여 표시
  const history = filteredStocks.value
    .filter(s => s.ticker === ticker)
    .sort((a, b) => a.date.localeCompare(b.date));

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: history.map(h => h.date),
      datasets: [{
        label: `${ticker} Price History`,
        data: history.map(h => h.usd_price),
        borderColor: '#409eff',
        backgroundColor: 'rgba(64, 158, 255, 0.1)',
        fill: true,
        tension: 0.3
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
};

onMounted(fetchStocks);
</script>

<style scoped>
.dashboard-wrapper { height: 100vh; background-color: #f5f7fa; display: flex; overflow: hidden; }
.sidebar { background: #fff; border-right: 1px solid #dcdfe6; padding: 20px; box-shadow: 2px 0 8px rgba(0,0,0,0.05); }
.brand { color: #409eff; font-size: 1.4rem; margin-bottom: 25px; text-align: center; font-weight: bold; }
.main-content { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.scroll-area { padding: 20px; overflow-y: auto; }
.section-card { margin-bottom: 20px; border-radius: 8px; }
.title-text { font-weight: bold; font-size: 16px; color: #303133; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.chart-container { height: 350px; }
.canvas-wrapper { height: 280px; }
.w-100 { width: 100%; }
.mx-1 { margin-left: 4px; margin-right: 4px; }
</style>