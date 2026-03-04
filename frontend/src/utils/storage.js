const TOKEN_KEY = 'datapivot_token'
const USER_KEY = 'datapivot_user'

export const storage = {
  // Token 操作
  getToken() {
    return localStorage.getItem(TOKEN_KEY)
  },

  setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
  },

  removeToken() {
    localStorage.removeItem(TOKEN_KEY)
  },

  // 用户信息操作
  getUser() {
    const user = localStorage.getItem(USER_KEY)
    return user ? JSON.parse(user) : null
  },

  setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },

  removeUser() {
    localStorage.removeItem(USER_KEY)
  },

  // 清空所有
  clear() {
    this.removeToken()
    this.removeUser()
  }
}
