import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/DashboardView.vue') },
      { path: 'orders', name: 'Orders', component: () => import('@/views/OrdersListView.vue') },
      { path: 'orders/new', name: 'OrderCreate', component: () => import('@/views/OrderCreateView.vue') },
      { path: 'orders/:id', name: 'OrderDetail', component: () => import('@/views/OrderDetailView.vue') },
      { path: 'users', name: 'Users', component: () => import('@/views/UsersListView.vue'), meta: { adminOnly: true } },
      { path: 'clients', name: 'Clients', component: () => import('@/views/ClientsListView.vue') },
      { path: 'reports', name: 'Reports', component: () => import('@/views/ReportsView.vue') },
      { path: 'complaint', name: 'Complaint', component: () => import('@/views/ComplaintCheckView.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.guest && token) {
    next('/')
  } else if (to.meta.adminOnly) {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (user?.role !== 'admin') next('/')
    else next()
  } else {
    next()
  }
})

export default router
