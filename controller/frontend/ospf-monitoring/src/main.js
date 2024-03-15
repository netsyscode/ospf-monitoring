import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'
import App from './App.vue'
import router from './router'

const app = createApp(App).mount('#app')

app.use(router)

app.use(ElementPlus)
import 'virtual:windi.css'
app.mount('#app')
