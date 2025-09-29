import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '../views/Login.vue'
import ContractListView from '../views/ContractList.vue'
import ContractDetailView from '../views/ContractDetail.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/contracts'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/contracts',
      name: 'contracts',
      component: ContractListView,
      meta: { requiresAuth: true }
    },
    {
      path: '/contracts/:id',
      name: 'contract-detail',
      component: ContractDetailView,
      meta: { requiresAuth: true },
      props: true
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
