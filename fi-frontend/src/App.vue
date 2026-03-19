<template>
  <el-container class="dashboard-wrapper" v-loading="loading">
    <el-aside width="280px" class="sidebar">
      <div class="sidebar-header"><h2 class="brand">FI Analysis</h2></div>
      <el-button type="primary" class="w-100" @click="fetchStocks">데이터 강제 새로고침</el-button>
    </el-aside>

    <el-container class="main-content">
      <el-main class="scroll-area">
        <el-tag v-if="allRawData.length > 0" type="success" style="margin-bottom: 10px;">
          로드된 데이터: {{ allRawData.length }}건 (첫번째 종목: {{ allRawData[0].ticker }})
        </el-tag>

        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span class="title-text">전체 데이터 상세 (조회기간: {{ (!finalStartDate && !finalEndDate) ? '전체기간' : '필터적용' }})</span>
            </div>
          </template>
          
          <el-table :data="paginatedData" stripe border height="550" style="width: 100%">
            <el-table-column label="Ticker" width="100" fixed>
              <template #default="scope">{{ scope.row.ticker }}</template>
            </el-table-column>
            
            <el-table-column label="Date" width="110">
              <template #default="scope">{{ scope.row.date }}</template>
            </el-table-column>

            <el-table-column label="PER" width="90" align="right">
              <template #default="scope">{{ formatFixed(scope.row.per) }}</template>
            </el-table-column>
            <el-table-column label="PBR" width="90" align="right">
              <template #default="scope">{{ formatFixed(scope.row.pbr) }}</template>
            </el-table-column>
            <el-table-column label="PSR" width="90" align="right">
              <template #default="scope">{{ formatFixed(scope.row.psr) }}</template>
            </el-table-column>
            <el-table-column label="PCR" width="90" align="right">
              <template #default="scope">{{ formatFixed(scope.row.pcr) }}</template>
            </el-table-column>
            <el-table-column label="ROE" width="90" align="right">
              <template #default="scope">{{ formatFixed(scope.row.roe) }}</template>
            </el-table-column>
            <el-table-column label="EPS" width="90" align="right">
              <template #default="scope">{{ formatFixed(scope.row.eps) }}</template>
            </el-table-column>
            <el-table-column label="PEG" width="80" align="right">
              <template #default="scope">{{ formatFixed(scope.row.peg) }}</template>
            </el-table-column>
            <el-table-column label="배당수익률" width="110" align="right">
              <template #default="scope">{{ formatFixed(scope.row.dividend_yield) }}</template>
            </el-table-column>
          </el-table>

          <div class="pagination-container" style="margin-top:20px; display:flex; justify-content:center;">
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
const finalStartDate = ref('');
const finalEndDate = ref('');

const API_URL = 'https://sj-fi.onrender.com/stocks';

// 숫자를 소수점 2자리로 고정하는 함수
const formatFixed = (val) => {
  if (val === undefined || val === null || val === '') return '-';
  const n = parseFloat(val);
  return isNaN(n) ? '-' : n.toFixed(2);
};

const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await axios.get(API_URL);
    // 백엔드 응답이 { history: [...] } 구조인지 다시 한 번 강제 확인
    if (response.data && response.data.history) {
      allRawData.value = [...response.data.history]; // 새 배열로 복사하여 반응성 트리거
    } else if (Array.isArray(response.data)) {
      allRawData.value = [...response.data];
    }
  } catch (error) {
    console.error("데이터 로드 실패:", error);
  } finally {
    loading.value = false;
  }
};

const filteredData = computed(() => {
  return allRawData.value.sort((a, b) => b.date.localeCompare(a.date));
});

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredData.value.slice(start, start + pageSize.value);
});

onMounted(fetchStocks);
</script>

<style scoped>
.dashboard-wrapper { height: 100vh; background-color: #f5f7fa; }
.sidebar { background: #fff; padding: 20px; border-right: 1px solid #dcdfe6; }
.main-content { flex: 1; overflow: hidden; }
.scroll-area { padding: 20px; height: 100%; overflow-y: auto; }
.w-100 { width: 100%; }
</style>