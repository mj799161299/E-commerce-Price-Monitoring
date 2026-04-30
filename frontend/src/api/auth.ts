import request from '@/utils/request'

export interface LoginData {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
}

// 用户登录
export const login = (data: LoginData) => {
  return request.post('/auth/login', data)
}

// 用户注册
export const register = (data: RegisterData) => {
  return request.post('/auth/register', data)
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return request.get('/auth/me')
}

// 更新用户信息
export const updateUser = (data: any) => {
  return request.put('/auth/me', data)
}
