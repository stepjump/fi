// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // router가 있다면 유지

// Element Plus 관련 추가
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(router) // router가 없다면 이 줄은 삭제
app.use(ElementPlus) // Element Plus 사용 등록

app.mount('#app')