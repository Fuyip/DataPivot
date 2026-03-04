import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

export function setupRouterGuards(router) {
  router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    // 设置页面标题
    document.title = to.meta.title
      ? `${to.meta.title} - DataPivot`
      : 'DataPivot'

    // 检查是否需要登录
    if (to.meta.requiresAuth !== false) {
      if (!authStore.isLoggedIn) {
        // 未登录，跳转到登录页
        next({
          path: '/login',
          query: { redirect: to.fullPath }
        })
        return
      }

      // 检查是否需要管理员权限
      if (to.meta.requiresAdmin && !authStore.isAdmin) {
        ElMessage.error('权限不足，需要管理员权限')
        next(from.path || '/dashboard')
        return
      }
    }

    // 已登录用户访问登录页，重定向到首页
    if (to.path === '/login' && authStore.isLoggedIn) {
      next('/dashboard')
      return
    }

    next()
  })
}
