import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getCurrentUser } from '@/api/auth'
import type { LoginData } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<any>(null)

  // 登录
  const login = async (data: LoginData) => {
    const res: any = await loginApi(data)
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    await fetchUserInfo()
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    const res: any = await getCurrentUser()
    userInfo.value = res
  }

  // 登出
  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    userInfo,
    login,
    logout,
    fetchUserInfo
  }
})
