<template>
  <div>
    <div v-if="loading" class="d-flex justify-content-center mt-5">
      <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="contract">
      <h3>Contract: {{ contract.name }}</h3>

      <div class="card mt-4">
        <div class="card-header">Contract Details</div>
        <div class="card-body">
            <p><strong>Budget Name:</strong> {{ contract.izin_prinsip_id[1] }}</p>
            <p><strong>Start Date:</strong> {{ contract.start_date }}</p>
            <p><strong>End Date:</strong> {{ contract.end_date }}</p>
        </div>
      </div>

      <h4 class="mt-5">Document Requirements</h4>
      <div class="accordion" id="terminAccordion">
        <div v-for="(termin, index) in termins" :key="termin.id" class="accordion-item">
          <h2 class="accordion-header" :id="`heading${termin.id}`">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" :data-bs-target="`#collapse${termin.id}`" :aria-expanded="index === 0 ? 'true' : 'false'" :aria-controls="`collapse${termin.id}`">
              {{ termin.name }}
            </button>
          </h2>
          <div :id="`collapse${termin.id}`" class="accordion-collapse collapse" :class="{ show: index === 0 }" :aria-labelledby="`heading${termin.id}`">
            <div class="accordion-body">
              <ul class="list-group">
                <li v-for="syarat in termin.syarat_termin_ids" :key="syarat.id" class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    {{ syarat.name }}
                    <a v-if="syarat.document" :href="getDownloadUrl(syarat.id, syarat.name)" target="_blank" class="ms-3">
                        <i class="fa fa-fw fa-download"></i> View Document
                    </a>
                  </div>
                  <div v-if="syarat.document" class="badge bg-success p-2">Completed</div>
                  <form v-else @submit.prevent="uploadDocument(syarat.id, $event)" class="d-flex">
                    <input type="file" class="form-control form-control-sm me-2" required>
                    <button type="submit" class="btn btn-sm btn-primary">Upload</button>
                  </form>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <h4 class="mt-5">Payment History</h4>
       <table class="table table-striped mt-3">
        <thead>
            <tr>
                <th>Number</th>
                <th>Date</th>
                <th class="text-end">Amount</th>
                <th class="text-center">Status</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="payment in payments" :key="payment.id">
                <td>{{ payment.name }}</td>
                <td>{{ payment.tanggal }}</td>
                <td class="text-end">{{ formatCurrency(payment.amount) }}</td>
                <td class="text-center"><span class="badge bg-info">{{ payment.state }}</span></td>
            </tr>
        </tbody>
       </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import odooService from '@/services/odoo'

const route = useRoute()
const contract = ref(null)
const termins = ref([])
const payments = ref([])
const loading = ref(true)
const error = ref('')

const ODOO_URL = import.meta.env.VITE_ODOO_URL;

const contractId = parseInt(route.params.id)

const fetchData = async () => {
  try {
    loading.value = true;
    // Fetch main contract details
    const contractData = await odooService.read('vit.kontrak', [contractId], ['name', 'start_date', 'end_date', 'izin_prinsip_id', 'termin_ids', 'payment_ids', 'currency_id']);
    if (!contractData || contractData.length === 0) {
      throw new Error('Contract not found.');
    }
    contract.value = contractData[0];

    // Fetch termins and their syarat_termins
    if (contract.value.termin_ids.length > 0) {
        const terminData = await odooService.searchRead('vit.termin', [['id', 'in', contract.value.termin_ids]], ['name', 'syarat_termin_ids']);
        for (let termin of terminData) {
            if (termin.syarat_termin_ids.length > 0) {
                termin.syarat_termin_ids = await odooService.searchRead('vit.syarat_termin', [['id', 'in', termin.syarat_termin_ids]], ['name', 'document']);
            }
        }
        termins.value = terminData;
    }

    // Fetch payments
    if (contract.value.payment_ids.length > 0) {
        payments.value = await odooService.searchRead('vit.payment', [['id', 'in', contract.value.payment_ids]], ['name', 'tanggal', 'amount', 'state']);
    }

  } catch (err) {
    error.value = 'Failed to load contract details.';
    console.error(err);
  } finally {
    loading.value = false;
  }
}

const uploadDocument = async (syaratId, event) => {
    const file = event.target[0].files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = async () => {
        const base64File = reader.result.split(',')[1];
        try {
            const success = await odooService.write('vit.syarat_termin', syaratId, { document: base64File });
            if (success) {
                // Refresh data to show the update
                fetchData();
            } else {
                alert('File upload failed.');
            }
        } catch (err) {
            alert('An error occurred during upload.');
        }
    };
    reader.onerror = (error) => {
        alert('Error reading file.');
    };
}

const getDownloadUrl = (syaratId, syaratName) => {
    // Odoo's default URL for downloading binary field content
    return `${ODOO_URL}/web/content/vit.syarat_termin/${syaratId}/document?download=true&field=document&filename=${syaratName}`;
}

const formatCurrency = (amount) => {
    // Basic currency formatting, assumes the currency from the contract.
    // A more robust solution would use the currency symbol from contract.value.currency_id
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
}

onMounted(fetchData);

</script>

<style scoped>
.accordion-button:not(.collapsed) {
    color: #0c63e4;
    background-color: #e7f1ff;
}
</style>