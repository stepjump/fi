<template>
  <el-container class="layout-container">
    <el-header>
      <div class="header-content">
        <h1 class="title">주식 실시간 모니터링 (Top 50)</h1>
        <el-button type="primary" @click="fetchStocks" :loading="loading">
          데이터 새로고침
        </el-button>
      </div>
    </el-header>

    <el-main>
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <el-empty v-else-if="stocks.length === 0" description="데이터를 불러올 수 없습니다." />

      <el-table 
        v-else 
        :data="stocks" 
        style="width: 100%" 
        stripe 
        highlight-current-row
        @current-change="handleRowClick"
      >
        <el-table-column prop="ticker" label="종목코드" width="120" sortable />
        
        <el-table-column label="현재가" align="right">
          <template #default="scope">
            {{ formatPrice(scope.row.price) }}
          </template>
        </el-table-column>

        <el-table-column label="변동률" align="right" width="120">
          <template #default="scope">
            <span :class="scope.row.change >= 0 ? 'text-red' : 'text-blue'">
              {{ scope.row.change >= 0 ? '+' : '' }}{{ scope.row.change.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="volume" label="거래량" align="right" sortable>
          <template #default="scope">
            {{ formatVolume(scope.row.volume) }}
          </template>
        </el-table-column>
      </el-table>
    </el-main>

    <el-footer>
      <p class="footer-text">© 2026 Stock Monitor. All rights reserved.</p>
    </el-footer>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus'; // 알림 메시지용

// 상태 변수 정의
const stocks = ref([]); // 주식 데이터 리스트
const loading = ref(false); // 로딩 상태

// ⚠️ 본인의 Render 백엔드 API 주소로 수정하세요!
const API_BASE_URL = 'https://sj-fi.onrender.com';

// 데이터를 백엔드에서 불러오는 함수
const fetchStocks = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${API_BASE_URL}/stocks`);
    // 백엔드 응답 형식이 { data: [...] } 인지 그냥 [...] 인지에 따라 수정 필요
    // 여기서는 그냥 리스트[...] 형태로 온다고 가정합니다.
    stocks.value = response.data; 
    ElMessage.success('데이터 업데이트 완료');
  } catch (error) {
    console.error("데이터 로딩 실패:", error);
    ElMessage.error('데이터를 불러오지 못했습니다. 백엔드 서버 상태를 확인하세요.');
  } finally {
    loading.value = false;
  }
};

// 표의 행(Row)을 클릭했을 때 상세 페이지로 이동하는 함수
const handleRowClick = (row) => {
  if (row) {
    // 나중에 상세 페이지(/stocks/{ticker})를 만들면 주석을 해제하세요.
    // router.push(`/stocks/${row.ticker}`); 
    ElMessage.info(`${row.ticker} 상세 페이지로 이동 예정`);
  }
};

// 숫자 포맷팅 함수들
const formatPrice = (value) => {
  if (!value) return '-';
  return value.toLocaleString('ko-KR', { style: 'currency', currency: 'KRW' });
};

const formatVolume = (value) => {
  if (!value) return '0';
  return value.toLocaleString('ko-KR');
};

// 화면이 처음 켜질 때 자동으로 데이터 로딩
onMounted(fetchStocks);
</script>

<style scoped>
/* CSS 스타일링 (Element Plus와 호환) */
.layout-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.el-header {
  background-color: #fff;
  color: #333;
  line-height: 60px;
  border-bottom: 1px solid #eee;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.el-main {
  padding: 20px 0;
}

.loading-container {
  padding: 40px;
}

.text-red {
  color: #f56c6c; /* Element Plus 빨간색 */
  font-weight: bold;
}

.text-blue {
  color: #409eff; /* Element Plus 파란색 */
  font-weight: bold;
}

.el-footer {
  text-align: center;
  color: #909399;
  border-top: 1px solid #eee;
  padding: 20px 0;
  margin-top: 20px;
}

.footer-text {
  font-size: 0.9rem;
}
</style>