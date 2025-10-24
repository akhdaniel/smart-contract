<template>
  <div id="app">
    <div v-if="loadingStore.isLoading" class="loading-overlay">
      <div class="spinner-border text-light" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <header>
      <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
          <a class="navbar-brand" href="/contracts"><i class="fa-solid fa-house me-2"></i>SmartContract Vendor Portal</a>
          <div v-if="authStore.isLoggedIn" class="d-flex align-items-center">
            <span class="me-3 text-secondary">Welcome, {{ authStore.user.name }}</span>
            <button @click="logout" class="btn btn-outline-secondary">Logout</button>
          </div>
        </div>
      </nav>
    </header>

    <main class="container mt-4">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useLoadingStore } from '@/stores/loading';

const authStore = useAuthStore()
const loadingStore = useLoadingStore();
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}
</style>
