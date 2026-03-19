<template>
  <el-container class="dashboard-wrapper" v-loading="loading">
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
        
        <div class="button-group">
          <el-button type="primary" class="sidebar-btn" @click="applyFilters">데이터 적용</el-button>
          <el-button type="info" class="sidebar-btn" @click="fetchStocks">새로고침</el-button>
        </div>
      </el-form>
    </el-aside>

    <el-container class="main-content">
      <el-main class="scroll-area">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span class="title-text">분석 결과 ({{ finalStartDate || '전체' }} ~ {{ finalEndDate || '전체' }})</span>
              <el-tag type="success">데이터: {{ filteredData.length }}건</el-tag>
            </div>
          </template>
          
          <el-table :data="paginatedData" stripe border height="550" style="width: 100%">
            <el-table-column label="Ticker" width="100" fixed>
              <template #default="scope">{{ scope.row.ticker }}</template>
            </el-table-column>
            
            <el-table-column label="Date" width="110">
              <template #default="scope">{{ scope.row.date }}</template>
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

            <el-table-column label="PER" width="85" align="right">
              <template #default="scope">{{ formatMetric(scope.row.per) }}</template>
            </el-table-column>
            <el-table-column label="PBR" width="85" align="right">
              <template #default="scope">{{ formatMetric(scope.row.pbr) }}</template>
            </el-table-column>
            <el-table-column label="PSR" width="85" align="right">
              <template #default="scope">{{ formatMetric(scope.row.psr) }}</template>
            </el-table-column>
            <el-table-column label="PCR" width="85" align="right">
              <template #default="scope">{{ formatMetric(scope.row.pcr) }}</template>
            </el-table-column>
            <el-table-column label="ROE" width="85" align="right">
              <template #default="scope">{{ formatMetric(scope.row.roe) }}</template>
            </el-table-column>
            <el-table-column label="EPS" width="90" align="right">
              <template #default="scope">{{ formatMetric(scope.row.eps) }}</template>
            </el-table-column>
            <el-table-column label="PEG" width="80" align="right">
              <template #default="scope">{{ formatMetric(scope.row.peg) }}</template>
            </el-table-column>
            <el-table-column label="Div.Yield" width="100" align="right">
              <template #default="scope">{{ formatMetric(scope.row.dividend_yield) }}</template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination v-model:current-page="currentPage" :page-size="pageSize" layout="prev, pager, next" :total="filteredData.length" />
          </div>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const allRawData = ref([]); 
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(50);
const startDate = ref('');
const endDate = ref('');
const finalStartDate = ref('');
const finalEndDate = ref('');

const API_URL = 'https://sj-fi.onrender.com/stocks';

// 가격 포맷팅
const formatCurrency = (val, prefix = '', suffix = '') => {
  if (val === undefined || val === null || val === '') return '-';
  return `${prefix}${parseFloat(val).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}${suffix}`;
};

// 일반 지표 포맷팅
const formatMetric = (val) => {
  if (val === undefined || val === null || val === '') return '-';
  const n = parseFloat(val);
  return isNaN(n) ? '-' : n.toFixed(2);
};

const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await axios.get(API_URL);
    // [핵심] JSON의 history 키 내부 데이터를 배열로 할당
    if (response.data && response.data.history) {
      allRawData.value = response.data.history;
    }
  } catch (error) {
    console.error("Fetch Error:", error);
  } finally {
    loading.value = false;
  }
};

const filteredData = computed(() => {
  return allRawData.value.filter(item => {
    if (finalStartDate.value && item.date < finalStartDate.value) return false;
    if (finalEndDate.value && item.date > finalEndDate.value) return false;
    return true;
  }).sort((a, b) => b.date.localeCompare(a.date));
});

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredData.value.slice(start, start + pageSize.value);
});

const applyFilters = () => {
  finalStartDate.value = startDate.value;
  finalEndDate.value = endDate.value;
  currentPage.value = 1;
};

onMounted(fetchStocks);
</script>

<style scoped>
.dashboard-wrapper { height: 100vh; display: flex; background-color: #f5f7fa; }
.sidebar { background: #fff; padding: 20px; border-right: 1px solid #dcdfe6; }
.main-content { flex: 1; overflow: hidden; }
.scroll-area { padding: 20px; height: 100%; overflow-y: auto; }
.currency-usd { color: #67c23a; font-weight: bold; }
.currency-krw { color: #409eff; font-weight: bold; }
.w-100 { width: 100%; }
.sidebar-btn { width: 100%; margin: 10px 0 0 0; }
.pagination-container { margin-top: 20px; display: flex; justify-content: center; }
</style>