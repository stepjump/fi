import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 한국어 로케일 추가
import ko from 'element-plus/dist/locale/ko.mjs'

const app = createApp(App)

// locale: ko 설정을 추가합니다.
app.use(ElementPlus, {
  locale: ko,
})

app.mount('#app')