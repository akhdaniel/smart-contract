<template>
  <div>
    <h3>Kontrak Saya</h3>
    <div v-if="loading" class="d-flex justify-content-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="contracts.length === 0" class="alert alert-info">
      Anda tidak memiliki kontrak.
    </div>
    <div v-else class="list-group">
      <router-link v-for="contract in contracts.records" :key="contract.id" :to="`/contracts/${contract.id}`" class="list-group-item list-group-item-action">
        <div class="d-flex w-100 justify-content-between">
          <h5 class="mb-1">{{ contract.name }}</h5>
        </div>
          <small>{{ contract.start_date }} - {{ contract.end_date }}</small>
        <p class="mb-1">Izin Prinzip: {{ contract.izin_prinsip_id.display_name }}</p>
        <p class="mb-1">Budget: {{ contract.budget_rkap_id.display_name }}</p>
        <div class="syarat-ribbon bg-success p-2">{{ contract.stage_id.display_name }}</div>

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
    const domain = [];
    const fieldsString = 'name,start_date,end_date,izin_prinsip_id,budget_rkap_id,stage_id';
    const specification = {
      name:{},
      start_date:{},
      end_date:{},
      izin_prinsip_id:{},
      budget_rkap_id:{},
      stage_id:{}
    }
    const result = await odooService.searchRead('vit.kontrak', domain, specification);
    console.log('result===',result)
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

<style scoped>
.syarat-ribbon {
    position: absolute;
    top: 0;
    right: 0;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    font-weight: bold;
    color: white;
    text-align: center;
    white-space: nowrap;
    border-radius: 0 0 0 0.25rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    z-index: 1;
}
</style>
