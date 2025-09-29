<template>
  <div>
    <h3>Daftar Kontrak</h3>
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
        <p class="mb-1"><strong>Start / End Date</strong>: {{ contract.start_date }} - {{ contract.end_date }}</p>
        <p class="mb-1"><strong>Izin Prinzip:</strong> {{ contract.izin_prinsip_id.display_name }}</p>
        <p class="mb-1"><strong>Budget:</strong> {{ contract.budget_rkap_id.display_name }}</p>
        <div class="syarat-ribbon p-2" :class="{ 'bg-warning': contract.stage_id.display_name.toLowerCase() === 'draft', 'bg-success': contract.stage_id.display_name.toLowerCase() === 'on progress', 'bg-secondary': contract.stage_id.display_name.toLowerCase() === 'done' }">{{ contract.stage_id.display_name }}</div>

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
      izin_prinsip_id:{
        fields:{display_name:{}}
      },
      budget_rkap_id:{
        fields:{display_name:{}}
      },
      stage_id:{
        fields:{display_name:{}}
      }
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

</style>
