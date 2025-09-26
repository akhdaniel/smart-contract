import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import odooService from '@/services/odoo'

export const useAuthStore = defineStore('auth', () => {
  const uid = ref(localStorage.getItem('uid'))
  const user = ref(JSON.parse(localStorage.getItem('user')))

  const isLoggedIn = computed(() => !!uid.value)

  async function login(username, password) {
    const result = await odooService.login(username, password)
    console.log('result-----',result)
    if (result) {
      uid.value = result.uid
      user.value = result.user_context
      localStorage.setItem('uid', uid.value)
      localStorage.setItem('user', JSON.stringify(user.value))
      return true
    } else {
      return false
    }
  }

  function logout() {
    uid.value = null
    user.value = null
    localStorage.removeItem('uid')
    localStorage.removeItem('user')
  }

  return { uid, user, isLoggedIn, login, logout }
})
