import request from './request'

export const authApi = {
  // 登录
  login(data) {
    return request.post('/v1/auth/login', data)
  },

  // 登出
  logout() {
    return request.post('/v1/auth/logout')
  },

  // 刷新 Token
  refreshToken() {
    return request.post('/v1/auth/refresh')
  },

  // 获取当前用户信息
  getCurrentUser() {
    return request.get('/v1/auth/me')
  }
}
