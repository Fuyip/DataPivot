import axios from 'axios'
import { ElMessage } from 'element-plus'
import { storage } from '@/utils/storage'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 是否正在刷新 Token
let isRefreshing = false
// 待重试的请求队列
let requestQueue = []

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = storage.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const { code, message, data } = response.data

    // 后端统一返回格式：{code, message, data}
    if (code === 200) {
      return data
    } else {
      ElMessage.error(message || '请求失败')
      return Promise.reject(new Error(message))
    }
  },
  async error => {
    // 422 验证错误
    if (error.response?.status === 422) {
      const detail = error.response?.data?.detail
      if (detail) {
        if (Array.isArray(detail)) {
          // FastAPI 验证错误格式
          const messages = detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join('; ')
          ElMessage.error(messages)
        } else if (typeof detail === 'string') {
          ElMessage.error(detail)
        }
      } else {
        ElMessage.error('请求参数验证失败')
      }
      return Promise.reject(error)
    }

    // 401 未授权：Token 过期或无效
    if (error.response?.status === 401) {
      const config = error.config

      // 避免刷新 Token 接口本身失败导致死循环
      if (config.url.includes('/auth/refresh')) {
        storage.clear()
        window.location.href = '/login'
        ElMessage.error('登录已过期，请重新登录')
        return Promise.reject(error)
      }

      // 如果正在刷新 Token，将请求加入队列
      if (isRefreshing) {
        return new Promise(resolve => {
          requestQueue.push(() => {
            config.headers.Authorization = `Bearer ${storage.getToken()}`
            resolve(request(config))
          })
        })
      }

      isRefreshing = true

      try {
        // 尝试刷新 Token
        const { data } = await axios.post(
          `${request.defaults.baseURL}/v1/auth/refresh`,
          {},
          {
            headers: {
              Authorization: `Bearer ${storage.getToken()}`
            }
          }
        )

        if (data.code === 200) {
          // 保存新 Token
          storage.setToken(data.data.access_token)

          // 重试队列中的请求
          requestQueue.forEach(cb => cb())
          requestQueue = []

          // 重试当前请求
          config.headers.Authorization = `Bearer ${data.data.access_token}`
          return request(config)
        } else {
          throw new Error('刷新 Token 失败')
        }
      } catch (refreshError) {
        // 刷新失败，清空状态并跳转登录
        storage.clear()
        window.location.href = '/login'
        ElMessage.error('登录已过期，请重新登录')
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // 403 权限不足
    if (error.response?.status === 403) {
      ElMessage.error('权限不足')
    }

    // 其他错误
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else if (error.message) {
      ElMessage.error(error.message)
    }

    return Promise.reject(error)
  }
)

export default request
