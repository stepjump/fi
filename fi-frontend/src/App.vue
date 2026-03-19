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

        <div class="button-group">
          <el-button type="primary" class="sidebar-btn" @click="applyFilters" :disabled="loading">
            데이터 적용 및 새로고침
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
                  📅 {{ (!finalStartDate && !finalEndDate) ? '전체기간' : (finalStartDate + ' ~ ' + finalEndDate) }}
                </el-tag>
              </div>
              <el-tag type="success">검색 결과: {{ filteredData.length }}건</el-tag>
            </div>
          </template>
          
          <el-table :data="paginatedData" stripe height="500" border style="width: 100%" highlight-current-row>
            <el-table-column prop="ticker" label="Ticker" width="90" fixed sortable />
            <el-table-column prop="name" label="Name" width="100" show-overflow-tooltip />
            <el-table-column prop="date" label="Date" width="110" sortable />
            
            <el-table-column prop="per" label="PER" width="85" align="right" sortable>
              <template #default="scope">{{ formatNum(scope.row.per) }}</template>
            </el-table-column>
            <el-table-column prop="pbr" label="PBR" width="85" align="right" sortable>
              <template #default="scope">{{ formatNum(scope.row.pbr) }}</template>
            </el-table-column>
            <el-table-column prop="psr" label="PSR" width="85" align="right" sortable>
              <template #default="scope">{{ formatNum(scope.row.psr) }}</template>
            </el-table-column>
            <el-table-column prop="pcr" label="PCR" width="85" align="right" sortable>
              <template #default="scope">{{ formatNum(scope.row.pcr) }}</template>
            </el-table-column>
            <el-table-column prop="roe" label="ROE" width="85" align="right" sortable>
              <template #default="scope">{{ formatNum(scope.row.roe) }}</template>
            </el-table-column>
            <el-table-column prop="eps" label="EPS" width="90" align="right" sortable>
              <template #default="scope">{{ formatNum(scope.row.eps) }}</template>
            </el-table-column>
            <el-table-column prop="peg" label="PEG" width="80" align="right" sortable>
              <template #default="scope">{{ formatNum(scope.row.peg) }}</template>
            </el-table-column>
            <el-table-column prop="dividend_yield" label="Div.Y(%)" width="100" align="right" sortable>
              <template #default="scope">{{ formatNum(scope.row.dividend_yield) }}</template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" layout="total, prev, pager, next" :total="filteredData.length" />
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

// 숫자 포맷팅 유틸리티
const formatNum = (val) => {
  if (val === undefined || val === null || val === '') return '-';
  const n = parseFloat(val);
  return isNaN(n) ? '-' : n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

// [가장 중요] 데이터 로드 로직
const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await axios.get(API_URL);
    // JSON 구조 { "history": [...] } 이므로 .history를 명시해야 합니다.
    if (response.data && response.data.history) {
      allRawData.value = response.data.history;
    } else {
      console.error("구조 오류: 'history' 키를 찾을 수 없음", response.data);
      allRawData.value = [];
    }
  } catch (error) {
    console.error("API 로드 실패:", error);
  } finally {
    loading.value = false;
  }
};

const filteredData = computed(() => {
  // allRawData가 객체가 아닌 배열임을 보장하며 필터링
  if (!Array.isArray(allRawData.value)) return [];
  
  return allRawData.value.filter(item => {
    const d = item.date || '';
    if (finalStartDate.value && d < finalStartDate.value) return false;
    if (finalEndDate.value && d > finalEndDate.value) return false;
    return true;
  }).sort((a, b) => (b.date || '').localeCompare(a.date || ''));
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
/* 이전 스타일과 동일 */
.dashboard-wrapper { height: 100vh; background-color: #f5f7fa; display: flex; overflow: hidden; }
.sidebar { background: #fff; border-right: 1px solid #dcdfe6; padding: 20px; }
.main-content { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.scroll-area { padding: 20px; overflow-y: auto; }
.section-card { border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.w-100 { width: 100%; }
.sidebar-btn { width: 100%; margin-top: 10px; }
.pagination-container { margin-top: 15px; display: flex; justify-content: center; }
</style>