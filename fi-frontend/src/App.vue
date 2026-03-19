<template>
  <el-container class="dashboard-wrapper" v-loading="loading" element-loading-text="데이터를 분석 중입니다...">
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
        
        <div class="button-group">
          <el-button type="primary" class="sidebar-btn" @click="applyFilters" :disabled="loading">
            데이터 적용 및 새로고침
          </el-button>
          
          <el-button type="success" class="sidebar-btn" @click="exportToExcel" :disabled="loading || filteredData.length === 0">
            엑셀 데이터 내보내기
          </el-button>
        </div>
      </el-form>
    </el-aside>

    <el-container class="main-content">
      <el-main class="scroll-area">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <span class="title-text">전체 데이터 상세 영역</span>
                <el-tag type="info" effect="plain" class="date-range-badge">
                  📅 
                  <template v-if="finalStartDate && finalEndDate">
                    {{ finalStartDate }} ~ {{ finalEndDate }}
                  </template>
                  <template v-else>
                    전체기간
                  </template>
                </el-tag>
              </div>
              <el-tag type="success">검색 결과: {{ filteredData.length }}건</el-tag>
            </div>
          </template>
          
          <el-table :data="paginatedData" stripe height="450" border style="width: 100%" highlight-current-row @current-change="handleRowClick">
            <el-table-column label="No." width="60" align="center" fixed>
              <template #default="scope">
                {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
              </template>
            </el-table-column>

            <el-table-column label="Ticker" width="90" fixed sortable>
              <template #default="scope">{{ scope.row.ticker || scope.row.Ticker || scope.row.TICKER }}</template>
            </el-table-column>
            
            <el-table-column label="Name" width="120" show-overflow-tooltip>
              <template #default="scope">{{ scope.row.name || scope.row.Name || scope.row.NAME }}</template>
            </el-table-column>

            <el-table-column label="Date" width="110" sortable>
              <template #default="scope">{{ scope.row.date || scope.row.Date || scope.row.DATE }}</template>
            </el-table-column>
            
            <el-table-column label="USD Price" width="110" align="right">
              <template #default="scope">
                <span class="currency-usd">{{ formatCurrency(scope.row.usd_price || scope.row.USD_PRICE || scope.row.price, '$') }}</span>
              </template>
            </el-table-column>

            <el-table-column label="KRW Price" width="120" align="right">
              <template #default="scope">
                <span class="currency-krw">{{ formatCurrency(scope.row.krw_price || scope.row.KRW_PRICE, '', '원') }}</span>
              </template>
            </el-table-column>

            <el-table-column label="PER" width="80" align="right" sortable>
              <template #default="scope">{{ scope.row.per || scope.row.PER || '-' }}</template>
            </el-table-column>
            <el-table-column label="PBR" width="80" align="right" sortable>
              <template #default="scope">{{ scope.row.pbr || scope.row.PBR || '-' }}</template>
            </el-table-column>
            <el-table-column label="PSR" width="80" align="right" sortable>
              <template #default="scope">{{ scope.row.psr || scope.row.PSR || '-' }}</template>
            </el-table-column>
            <el-table-column label="PCR" width="80" align="right" sortable>
              <template #default="scope">{{ scope.row.pcr || scope.row.PCR || '-' }}</template>
            </el-table-column>
            <el-table-column label="ROE(%)" width="90" align="right" sortable>
              <template #default="scope">{{ scope.row.roe || scope.row.ROE || '-' }}</template>
            </el-table-column>
            <el-table-column label="EPS" width="100" align="right" sortable>
              <template #default="scope">{{ scope.row.eps || scope.row.EPS || '-' }}</template>
            </el-table-column>
            <el-table-column label="PEG" width="80" align="right" sortable>
              <template #default="scope">{{ scope.row.peg || scope.row.PEG || '-' }}</template>
            </el-table-column>
            <el-table-column label="Div.Y(%)" width="100" align="right" sortable>
              <template #default="scope">{{ scope.row.dividend_yield || scope.row.DIVIDEND_YIELD || '-' }}</template>
            </el-table-column>
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
          <template #header>
            <div class="card-header">
              <span class="title-text">가격 추이 분석 (KRW / USD 비교)</span>
              <el-tag v-if="selectedStock" type="info">{{ selectedStock.ticker || selectedStock.Ticker }} 분석 중</el-tag>
            </div>
          </template>
          <div class="canvas-wrapper"><canvas id="mainPriceChart"></canvas></div>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import Chart from 'chart.js/auto';
import * as XLSX from 'xlsx';

const allRawData = ref([]); 
const loading = ref(false);
const selectedStock = ref(null);
let chartInstance = null;

const currentPage = ref(1);
const pageSize = ref(50);

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

const formatCurrency = (val, prefix = '', suffix = '') => {
  if (val === undefined || val === null || val === '') return prefix + ' - ' + suffix;
  const num = parseFloat(val);
  if (isNaN(num)) return prefix + ' - ' + suffix;
  return `${prefix}${num.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}${suffix}`;
};

const tickerList = computed(() => {
  const tickers = allRawData.value.map(item => (item.ticker || item.Ticker || item.TICKER || '').trim().toUpperCase());
  return [...new Set(tickers)].filter(Boolean).sort();
});

const filteredData = computed(() => {
  return allRawData.value.filter(item => {
    const t = (item.ticker || item.Ticker || item.TICKER || '').trim().toUpperCase();
    const d = item.date || item.Date || item.DATE || '';
    const roeVal = parseFloat(item.roe || item.ROE || 0);
    const perVal = parseFloat(item.per || item.PER || 0);

    if (finalStartDate.value && d < finalStartDate.value) return false;
    if (finalEndDate.value && d > finalEndDate.value) return false;
    if (finalSearchQuery.value && t !== finalSearchQuery.value) return false;
    if (finalFilterBlueChip.value && roeVal < 15) return false;
    if (finalFilterLowPer.value && (perVal <= 0 || perVal >= 15)) return false;

    return true;
  }).sort((a, b) => (b.date || b.Date || '').localeCompare(a.date || a.Date || ''));
});

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredData.value.slice(start, start + pageSize.value);
});

const exportToExcel = () => {
  if (filteredData.value.length === 0) return;
  const exportData = filteredData.value.map((item, index) => ({
    "No": index + 1,
    "Ticker": item.ticker || item.Ticker || item.TICKER,
    "Name": item.name || item.Name || item.NAME,
    "Date": item.date || item.Date || item.DATE,
    "Price(USD)": item.usd_price || item.USD_PRICE || item.price,
    "Price(KRW)": item.krw_price || item.KRW_PRICE,
    "PER": item.per || item.PER,
    "PBR": item.pbr || item.PBR,
    "PSR": item.psr || item.PSR,
    "PCR": item.pcr || item.PCR,
    "ROE(%)": item.roe || item.ROE,
    "EPS": item.eps || item.EPS,
    "PEG": item.peg || item.PEG,
    "Div.Yield(%)": item.dividend_yield || item.DIVIDEND_YIELD
  }));
  const worksheet = XLSX.utils.json_to_sheet(exportData);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "StockData");
  XLSX.writeFile(workbook, `FI_Data_${new Date().toISOString().slice(0, 10)}.xlsx`);
};

const applyFilters = () => {
  currentPage.value = 1;
  finalStartDate.value = startDate.value;
  finalEndDate.value = endDate.value;
  finalSearchQuery.value = tempSearchQuery.value;
  finalFilterBlueChip.value = tempFilterBlueChip.value;
  finalFilterLowPer.value = tempFilterLowPer.value;
  if (allRawData.value.length === 0) fetchStocks();
};

const handleSizeChange = (val) => { pageSize.value = val; currentPage.value = 1; };
const handleCurrentChange = (val) => { currentPage.value = val; };

const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await axios.get(API_URL);
    allRawData.value = Array.isArray(response.data) ? response.data : (response.data.stocks || []);
  } catch (error) {
    console.error("Fetch Error:", error);
  } finally {
    loading.value = false;
  }
};

const handleRowClick = (row) => {
  if (row) {
    selectedStock.value = row;
    updateChart(row.ticker || row.Ticker || row.TICKER);
  }
};

const updateChart = (ticker) => {
  const ctx = document.getElementById('mainPriceChart')?.getContext('2d');
  if (!ctx || !ticker) return;
  if (chartInstance) chartInstance.destroy();

  const history = allRawData.value
    .filter(s => (s.ticker || s.Ticker || s.TICKER) === ticker)
    .sort((a, b) => (a.date || a.Date || a.DATE).localeCompare(b.date || b.Date || b.DATE))
    .slice(-30);

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: history.map(h => h.date || h.Date || h.DATE),
      datasets: [
        {
          label: 'KRW Price (원)',
          data: history.map(h => h.krw_price || h.KRW_PRICE || 0),
          borderColor: '#409eff',
          yAxisID: 'y-krw',
          tension: 0.3
        },
        {
          label: 'USD Price ($)',
          data: history.map(h => h.usd_price || h.USD_PRICE || h.price || 0),
          borderColor: '#67c23a',
          yAxisID: 'y-usd',
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        'y-krw': { type: 'linear', position: 'left' },
        'y-usd': { type: 'linear', position: 'right', grid: { drawOnChartArea: false } }
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
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; gap: 15px; }
.date-range-badge { font-weight: bold; font-size: 0.85rem; padding: 0 12px; }
.pagination-container { margin-top: 15px; display: flex; justify-content: center; }
.chart-container { height: 350px; }
.canvas-wrapper { height: 280px; }
.w-100 { width: 100%; }
.button-group { margin-top: 20px; display: flex; flex-direction: column; gap: 10px; }
.sidebar-btn { width: 100% !important; margin-left: 0 !important; margin-right: 0 !important; display: block; }
.currency-usd { color: #67c23a; font-weight: bold; }
.currency-krw { color: #409eff; font-weight: bold; }
</style>