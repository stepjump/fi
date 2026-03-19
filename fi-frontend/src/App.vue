<template>
  <el-container class="dashboard-wrapper" v-loading="loading" element-loading-text="데이터를 정제 중입니다... 잠시만 기다려주세요.">
    <el-aside width="280px" class="sidebar">
      <div class="sidebar-header"><h2 class="brand">FI Analysis</h2></div>
      
      <el-form class="filter-form" label-position="top" @submit.prevent>
        <el-divider content-position="left">조회 기간</el-divider>
        <el-form-item label="시작일자">
          <el-date-picker v-model="startDate" type="date" placeholder="시작일" format="YYYY-MM-DD" value-format="YYYY-MM-DD" class="w-100" />
        </el-form-item>
        <el-form-item label="종료일자">
          <el-date-picker v-model="endDate" type="date" placeholder="종료일" format="YYYY-MM-DD" value-format="YYYY-MM-DD" class="w-100" />
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
        
        <el-button type="primary" class="w-100" @click="applyFilters" :disabled="loading">
          {{ loading ? '처리 중...' : '데이터 적용 및 새로고침' }}
        </el-button>
      </el-form>
    </el-aside>

    <el-container class="main-content">
      <el-main class="scroll-area">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span class="title-text">전체 데이터 영역</span>
              <div>
                <el-tag v-if="finalStartDate || finalEndDate" type="warning" class="mx-1">
                  {{ finalStartDate || '시작' }} ~ {{ finalEndDate || '종료' }}
                </el-tag>
                <el-tag type="success">검색 결과: {{ filteredStocks.length }}건</el-tag>
              </div>
            </div>
          </template>
          
          <el-table 
            :data="filteredStocks" 
            stripe 
            height="500" 
            border 
            style="width: 100%"
            @current-change="handleRowClick"
            :empty-text="loading ? '데이터를 불러오는 중...' : '조건에 맞는 데이터가 없습니다.'"
          >
            <el-table-column prop="ticker" label="Ticker" width="100" fixed sortable />
            <el-table-column prop="name" label="Name" width="130" show-overflow-tooltip />
            <el-table-column prop="date" label="Date" width="110" sortable />
            <el-table-column label="USD Price" width="110" align="right">
              <template #default="scope">{{ formatDecimal(scope.row.usd_price || scope.row.price) }}</template>
            </el-table-column>
            <el-table-column label="KRW Price" width="120" align="right">
              <template #default="scope">{{ formatDecimal(scope.row.krw_price) }}</template>
            </el-table-column>
            <el-table-column prop="per" label="PER" width="80" align="right" sortable />
            <el-table-column prop="roe" label="ROE (%)" width="90" align="right" sortable />
            <el-table-column prop="peg" label="PEG" width="80" align="right" sortable />
            <el-table-column prop="dividend_yield" label="Div.Y" width="90" align="right" sortable />
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
  if (val === undefined || val === null || val === 0) return '0.0000';
  const num = parseFloat(val);
  return isNaN(num) ? '0.0000' : num.toFixed(4);
};

// 콤보박스용 유니크 티커 목록 (성능 최적화: Set 사용)
const tickerList = computed(() => {
  const tickers = allRawData.value.map(item => (item.ticker || item.Ticker || item.symbol || '').trim().toUpperCase());
  return [...new Set(tickers)].filter(Boolean).sort();
});

// 필터링 로직 최적화 (불필요한 루프 제거)
const filteredStocks = computed(() => {
  if (allRawData.value.length === 0) return [];

  return allRawData.value.filter(item => {
    const t = (item.ticker || item.Ticker || '').trim().toUpperCase();
    const d = item.date || item.Date || '';
    const roe = parseFloat(item.roe || item.ROE || 0);
    const per = parseFloat(item.per || item.PER || 0);

    // 1. 기간 필터
    if (finalStartDate.value && d < finalStartDate.value) return false;
    if (finalEndDate.value && d > finalEndDate.value) return false;
    
    // 2. 종목 필터
    if (finalSearchQuery.value && t !== finalSearchQuery.value) return false;
    
    // 3. 지표 필터
    if (finalFilterBlueChip.value && roe < 15) return false;
    if (finalFilterLowPer.value && (per <= 0 || per >= 15)) return false;

    return true;
  }).sort((a, b) => (b.date || '').localeCompare(a.date || '')); 
});

const applyFilters = async () => {
  finalStartDate.value = startDate.value;
  finalEndDate.value = endDate.value;
  finalSearchQuery.value = tempSearchQuery.value;
  finalFilterBlueChip.value = tempFilterBlueChip.value;
  finalFilterLowPer.value = tempFilterLowPer.value;
  
  // 데이터가 이미 로드되어 있다면 굳이 API를 다시 쏘지 않고 필터만 적용합니다.
  if (allRawData.value.length === 0) {
    await fetchStocks();
  }
};

const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await axios.get(API_URL, { timeout: 30000 }); // 30초 타임아웃
    allRawData.value = Array.isArray(response.data) ? response.data : (response.data.stocks || []);
    console.log("로드된 데이터 수:", allRawData.value.length);
  } catch (error) {
    console.error("데이터 로드 중 에러 발생:", error);
    alert("데이터를 가져오는 데 실패했습니다. 서버 상태를 확인하세요.");
  } finally {
    loading.value = false;
  }
};

const handleRowClick = (row) => {
  if (row) {
    selectedStock.value = row;
    updateChart(row.ticker || row.Ticker);
  }
};

const updateChart = (ticker) => {
  const ctx = document.getElementById('mainPriceChart')?.getContext('2d');
  if (!ctx || !ticker) return;
  if (chartInstance) chartInstance.destroy();

  // 차트용 데이터 추출 (최대 30개로 제한하여 성능 확보)
  const history = filteredStocks.value
    .filter(s => (s.ticker || s.Ticker) === ticker)
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(-30); 

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: history.map(h => h.date),
      datasets: [{
        label: `${ticker} Price Trend`,
        data: history.map(h => h.usd_price || h.price || h.PRICE),
        borderColor: '#409eff',
        tension: 0.3,
        fill: false
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
.brand { color: #409eff; font-size: 1.4rem; margin-bottom: 25px; text-align: center; font-weight: bold; }
.main-content { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.scroll-area { padding: 20px; overflow-y: auto; }
.section-card { margin-bottom: 20px; border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.chart-container { height: 350px; }
.canvas-wrapper { height: 280px; }
.w-100 { width: 100%; }
.mx-1 { margin-left: 4px; }
</style>