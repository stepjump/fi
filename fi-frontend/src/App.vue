<template>
  <el-container class="dashboard-wrapper" v-loading="loading" element-loading-text="데이터를 불러오는 중입니다...">
    <el-aside width="280px" class="sidebar">
      <div class="sidebar-header"><h2 class="brand">FI Analysis</h2></div>
      
      <el-form class="filter-form" label-position="top" @submit.prevent>
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
        
        <el-button type="primary" class="w-100" @click="applyFilters" :disabled="loading">
          데이터 적용 및 새로고침
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
                <el-tag type="success">검색 결과: {{ filteredData.length }}건</el-tag>
              </div>
            </div>
          </template>
          
          <el-table 
            :data="paginatedData" 
            stripe 
            height="450" 
            border 
            style="width: 100%" 
            highlight-current-row
            @current-change="handleRowClick"
          >
            <el-table-column label="No." width="70" align="center" fixed>
              <template #default="scope">
                {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
              </template>
            </el-table-column>

            <el-table-column prop="ticker" label="Ticker" width="100" fixed sortable />
            <el-table-column prop="name" label="Name" width="130" show-overflow-tooltip />
            <el-table-column prop="date" label="Date" width="110" sortable />
            
            <el-table-column label="USD Price" width="130" align="right">
              <template #default="scope">
                <span class="currency-usd">{{ formatCurrency(scope.row.usd_price || scope.row.price, '$') }}</span>
              </template>
            </el-table-column>

            <el-table-column label="KRW Price" width="140" align="right">
              <template #default="scope">
                <span class="currency-krw">{{ formatCurrency(scope.row.krw_price, '', '원') }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="per" label="PER" width="80" align="right" sortable />
            <el-table-column prop="roe" label="ROE (%)" width="90" align="right" sortable />
            <el-table-column prop="peg" label="PEG" width="80" align="right" sortable />
            <el-table-column prop="dividend_yield" label="Div.Y" width="90" align="right" sortable />
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredData.length"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
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

// --- 상태 정의 ---
const allRawData = ref([]); 
const loading = ref(false);
const selectedStock = ref(null);
let chartInstance = null;

// 페이지네이션 관련
const currentPage = ref(1);
const pageSize = ref(50);

// 필터 임시/최종 값
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

// --- 유틸리티 함수 ---

// 통화 포맷: 소수점 2자리 + 콤마 + 단위
const formatCurrency = (val, prefix = '', suffix = '') => {
  if (val === undefined || val === null || val === 0) return prefix + ' 0.00 ' + suffix;
  const num = parseFloat(val);
  if (isNaN(num)) return prefix + ' 0.00 ' + suffix;
  
  const parts = num.toFixed(2).split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return `${prefix}${parts.join('.')}${suffix}`;
};

// --- Computed 로직 (성능 최적화) ---

// 사이드바 콤보박스용 티커 리스트
const tickerList = computed(() => {
  const tickers = allRawData.value.map(item => (item.ticker || item.Ticker || '').trim().toUpperCase());
  return [...new Set(tickers)].filter(Boolean).sort();
});

// 전체 데이터 필터링 (메모리 부하 방지를 위해 필터링만 수행)
const filteredData = computed(() => {
  return allRawData.value.filter(item => {
    const t = (item.ticker || item.Ticker || '').trim().toUpperCase();
    const d = item.date || item.Date || '';
    const roe = parseFloat(item.roe || item.ROE || 0);
    const per = parseFloat(item.per || item.PER || 0);

    if (finalStartDate.value && d < finalStartDate.value) return false;
    if (finalEndDate.value && d > finalEndDate.value) return false;
    if (finalSearchQuery.value && t !== finalSearchQuery.value) return false;
    if (finalFilterBlueChip.value && roe < 15) return false;
    if (finalFilterLowPer.value && (per <= 0 || per >= 15)) return false;

    return true;
  }).sort((a, b) => (b.date || '').localeCompare(a.date || ''));
});

// 현재 페이지에 보여줄 데이터 조각
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredData.value.slice(start, end);
});

// --- 이벤트 핸들러 ---

const applyFilters = () => {
  currentPage.value = 1; // 필터 변경 시 무조건 1페이지로
  finalStartDate.value = startDate.value;
  finalEndDate.value = endDate.value;
  finalSearchQuery.value = tempSearchQuery.value;
  finalFilterBlueChip.value = tempFilterBlueChip.value;
  finalFilterLowPer.value = tempFilterLowPer.value;
  
  // 데이터가 없을 때만 새로 불러오고, 있을 때는 필터링만 적용(이미 Computed에서 처리됨)
  if (allRawData.value.length === 0) fetchStocks();
};

const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
};

const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await axios.get(API_URL, { timeout: 30000 });
    allRawData.value = Array.isArray(response.data) ? response.data : (response.data.stocks || []);
  } catch (error) {
    console.error("데이터 로드 실패:", error);
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

// 차트 업데이트 (Y축 KRW 표시)
const updateChart = (ticker) => {
  const ctx = document.getElementById('mainPriceChart')?.getContext('2d');
  if (!ctx || !ticker) return;
  if (chartInstance) chartInstance.destroy();

  // 선택된 종목의 전체 이력 (최대 50개)
  const history = filteredData.value
    .filter(s => (s.ticker || s.Ticker) === ticker)
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(-50);

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: history.map(h => h.date),
      datasets: [{
        label: `${ticker} 원화 가격 추이`,
        data: history.map(h => h.krw_price || 0),
        borderColor: '#409eff',
        backgroundColor: 'rgba(64, 158, 255, 0.1)',
        fill: true,
        tension: 0.3
      }]
    },
    options: { 
      responsive: true, 
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => `가격: ${context.parsed.y.toLocaleString()} 원`
          }
        }
      },
      scales: {
        y: {
          ticks: {
            callback: (val) => val.toLocaleString() + ' 원'
          }
        }
      }
    }
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
.pagination-container { margin-top: 20px; display: flex; justify-content: center; }
.chart-container { height: 380px; }
.canvas-wrapper { height: 320px; }
.w-100 { width: 100%; }
.mx-1 { margin-left: 4px; }
.currency-usd { color: #67c23a; font-weight: bold; font-family: 'Courier New', Courier, monospace; }
.currency-krw { color: #409eff; font-weight: bold; }
</style>