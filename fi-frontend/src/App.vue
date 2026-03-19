<template>
  <el-container class="dashboard-wrapper" v-loading="loading">
    <el-aside width="280px" class="sidebar">
      <div class="sidebar-header"><h2 class="brand">FI Analysis</h2></div>
      
      <div class="button-group" style="padding: 20px;">
        <el-button type="primary" class="w-100" @click="fetchStocks">데이터 새로고침</el-button>
      </div>
    </el-aside>

    <el-container class="main-content">
      <el-main class="scroll-area">
        <el-alert v-if="!loading && allRawData.length === 0" title="데이터를 불러오지 못했습니다." type="warning" description="API 연결 상태나 백엔드 응답 구조를 확인해주세요." show-icon style="margin-bottom: 20px;" />

        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>전체 데이터 상세 ({{ finalStartDate || '전체' }} ~ {{ finalEndDate || '전체' }})</span>
              <el-tag type="success">총 {{ filteredData.length }}건</el-tag>
            </div>
          </template>
          
          <el-table :data="paginatedData" stripe border height="500">
            <el-table-column prop="ticker" label="Ticker" width="100" fixed />
            <el-table-column prop="name" label="Name" width="120" />
            <el-table-column prop="date" label="Date" width="120" />
            
            <el-table-column prop="per" label="PER" align="right" />
            <el-table-column prop="pbr" label="PBR" align="right" />
            <el-table-column prop="psr" label="PSR" align="right" />
            <el-table-column prop="pcr" label="PCR" align="right" />
            <el-table-column prop="roe" label="ROE" align="right" />
            <el-table-column prop="eps" label="EPS" align="right" />
            <el-table-column prop="peg" label="PEG" align="right" />
            <el-table-column prop="dividend_yield" label="배당수익률" align="right" />
          </el-table>
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
const API_URL = 'https://sj-fi.onrender.com/stocks';

// 페이지네이션 및 필터 상태
const currentPage = ref(1);
const pageSize = ref(50);
const finalStartDate = ref('');
const finalEndDate = ref('');

// --- [가장 중요한 수정 부분] ---
const fetchStocks = async () => {
  loading.value = true;
  console.log("데이터 요청 시작...");
  try {
    const response = await axios.get(API_URL);
    console.log("응답 전체 데이터:", response.data);
    
    // 보내주신 JSON 구조 { "history": [...] } 를 정확히 타겟팅
    if (response.data && response.data.history) {
      allRawData.value = response.data.history;
      console.log("매핑된 데이터 수:", allRawData.value.length);
    } else {
      console.error("응답에 'history' 키가 없습니다.");
      allRawData.value = [];
    }
  } catch (error) {
    console.error("API 호출 실패:", error);
  } finally {
    loading.value = false;
  }
};

const filteredData = computed(() => {
  // 필터 로직 (날짜 위주)
  return allRawData.value.filter(item => {
    if (finalStartDate.value && item.date < finalStartDate.value) return false;
    if (finalEndDate.value && item.date > finalEndDate.value) return false;
    return true;
  });
});

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  return filteredData.value.slice(start, start + pageSize.value);
});

onMounted(fetchStocks);
</script>