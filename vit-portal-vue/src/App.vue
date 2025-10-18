<template>
  <header>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <a class="navbar-brand" href="/contracts"><i class="fa-solid fa-house me-2"></i>SmartContract Vendor Portal</a>
        <div v-if="authStore.isLoggedIn" class="d-flex align-items-center">
          <span class="me-3 fg-white">Welcome, {{ authStore.user.name }}</span>
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
