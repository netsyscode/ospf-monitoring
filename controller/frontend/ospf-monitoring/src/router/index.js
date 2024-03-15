import{
    createRouter,
    createWebHistory
} from 'vue-router'

import Index from '~/pages/index.vue' 
import About from '~/pages/about.vue'
import NotFund from '~/pages/404.vue'

const routes = [
    {
        path: '/',
        component: Index
    },{
        path: '/about',
        component: About
    },{
        path: '/:pathMatch(.*)*',
        component: NotFund,
        name: '404'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
    })

export default router