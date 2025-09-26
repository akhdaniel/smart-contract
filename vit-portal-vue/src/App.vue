<template>
  <header>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <div class="container">
        <a class="navbar-brand" href="#">Vendor Portal</a>
        <div v-if="authStore.isLoggedIn">
          <button @click="logout" class="btn btn-outline-secondary">Logout</button>
        </div>
      </div>
    </nav>
  </header>

  <main class="container mt-4">
    <RouterView />
  </main>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
