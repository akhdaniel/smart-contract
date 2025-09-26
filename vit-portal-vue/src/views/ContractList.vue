<template>
  <div>
    <h3>My Contracts</h3>
    <div v-if="loading" class="d-flex justify-content-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="contracts.length === 0" class="alert alert-info">
      You have no contracts.
    </div>
    <div v-else class="list-group">
      <router-link v-for="contract in contracts" :key="contract.id" :to="`/contracts/${contract.id}`" class="list-group-item list-group-item-action">
        <div class="d-flex w-100 justify-content-between">
          <h5 class="mb-1">{{ contract.name }}</h5>
          <small>{{ contract.start_date }}</small>
        </div>
        <p class="mb-1">{{ contract.izin_prinsip_id[1] }}</p>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import odooService from '@/services/odoo'
import { useAuthStore } from '@/stores/auth'

const contracts = ref([])
const loading = ref(true)
const error = ref('')
const authStore = useAuthStore()

onMounted(async () => {
  try {
    const partnerId = authStore.user.partner_id;
    const domain = [['partner_id', 'child_of', partnerId]];
    const fields = ['name', 'start_date', 'izin_prinsip_id'];
    const result = await odooService.searchRead('vit.kontrak', domain, fields);
    if (result) {
      contracts.value = result;
    } else {
      error.value = 'Could not fetch contracts.';
    }
  } catch (err) {
    error.value = 'An error occurred while fetching contracts.';
  }
  loading.value = false;
});
</script>
