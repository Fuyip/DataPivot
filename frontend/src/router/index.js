import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterGuards } from './guards'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login/index.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/components/Layout/AppLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'DataLine' }
      },
      {
        path: 'system/users',
        name: 'UserManagement',
        component: () => import('@/views/System/UserManagement/index.vue'),
        meta: {
          title: '用户管理',
          icon: 'User',
          requiresAdmin: true
        }
      },
      {
        path: 'system/cases',
        name: 'CaseManagement',
        component: () => import('@/views/System/CaseManagement/index.vue'),
        meta: {
          title: '案件管理',
          icon: 'FolderOpened',
          requiresAdmin: true
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 设置路由守卫
setupRouterGuards(router)

export default router
