import request from './request'

export const userApi = {
  // 获取用户列表
  getUserList(params) {
    return request.get('/v1/users', { params })
  },

  // 获取用户详情
  getUserDetail(id) {
    return request.get(`/v1/users/${id}`)
  },

  // 创建用户
  createUser(data) {
    return request.post('/v1/users', data)
  },

  // 更新用户
  updateUser(id, data) {
    return request.put(`/v1/users/${id}`, data)
  },

  // 删除用户
  deleteUser(id) {
    return request.delete(`/v1/users/${id}`)
  },

  // 修改用户角色
  updateUserRole(id, role) {
    return request.put(`/v1/users/${id}/role`, null, {
      params: { role }
    })
  },

  // 重置用户密码
  resetPassword(id, newPassword) {
    return request.put(`/v1/users/${id}/password`, null, {
      params: { new_password: newPassword }
    })
  }
}
