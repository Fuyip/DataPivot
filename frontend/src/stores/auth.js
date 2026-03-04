import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { storage } from '@/utils/storage'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(storage.getToken())
  const user = ref(storage.getUser())

  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 登录
  async function login(username, password) {
    try {
      const data = await authApi.login({ username, password })

      // 保存 Token 和用户信息
      token.value = data.access_token
      user.value = data.user

      storage.setToken(data.access_token)
      storage.setUser(data.user)

      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  // 登出
  async function logout() {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      // 清空状态
      token.value = null
      user.value = null
      storage.clear()
    }
  }

  // 刷新 Token
  async function refreshToken() {
    try {
      const data = await authApi.refreshToken()
      token.value = data.access_token
      storage.setToken(data.access_token)
      return true
    } catch (error) {
      console.error('Token 刷新失败:', error)
      return false
    }
  }

  // 获取用户信息
  async function fetchUserInfo() {
    try {
      const data = await authApi.getCurrentUser()
      user.value = data
      storage.setUser(data)
      return true
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return false
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    refreshToken,
    fetchUserInfo
  }
})
