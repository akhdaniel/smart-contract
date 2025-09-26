import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import odooService from '@/services/odoo'

export const useAuthStore = defineStore('auth', () => {
  const uid = ref(localStorage.getItem('uid'))
  const sid = ref(localStorage.getItem('sid')) // Session ID
  const user = ref(JSON.parse(localStorage.getItem('user')))

  const isLoggedIn = computed(() => !!uid.value && !!sid.value)

  async function login(username, password) {
    const result = await odooService.login(username, password)
    if (result) {
      uid.value = result.uid
      sid.value = result.sid
      user.value = result.user_context
      localStorage.setItem('uid', uid.value)
      localStorage.setItem('sid', sid.value)
      localStorage.setItem('user', JSON.stringify(user.value))
      // Set session id in axios headers for subsequent requests
      odooService.setSessionId(sid.value)
      return true
    } else {
      return false
    }
  }

  function logout() {
    uid.value = null
    sid.value = null
    user.value = null
    localStorage.removeItem('uid')
    localStorage.removeItem('sid')
    localStorage.removeItem('user')
    odooService.setSessionId(null)
  }

  return { uid, sid, user, isLoggedIn, login, logout }
})
