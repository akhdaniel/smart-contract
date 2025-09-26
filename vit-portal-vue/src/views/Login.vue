<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
      <div class="card mt-5">
        <div class="card-body">
          <h3 class="card-title text-center">Login</h3>
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label for="username" class="form-label">Username (Email)</label>
              <input type="text" class="form-control" id="username" v-model="username" required>
            </div>
            <div class="mb-3">
              <label for="password" class="form-label">Password</label>
              <input type="password" class="form-control" id="password" v-model="password" required>
            </div>
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Login
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const router = useRouter()
const authStore = useAuthStore()

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const success = await authStore.login(username.value, password.value)
    if (success) {
      router.push('/contracts')
    } else {
      error.value = 'Login failed. Please check your credentials.'
    }
  } catch (err) {
    error.value = 'An error occurred during login.'
  }
  loading.value = false
}
</script>
