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
      <div v-if="uploadError" class="alert alert-danger mt-3">{{ uploadError }}</div>
      <div class="accordion" id="terminAccordion">
        <div v-for="(termin, index) in termins" :key="termin.id" class="accordion-item">
          <h2 class="accordion-header" :id="`heading${termin.id}`">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" :data-bs-target="`#collapse${termin.id}`" :aria-expanded="index === 0 ? 'true' : 'false'" :aria-controls="`collapse${termin.id}`">
              {{ termin.name }}
            </button>
          </h2>
          <div :id="`collapse${termin.id}`" class="accordion-collapse collapse" :class="{ show: index === 0 }" :aria-labelledby="`heading${termin.id}`" data-bs-parent="#terminAccordion">
            <div class="accordion-body">
              <ul class="list-group">
                <li v-for="syarat in termin.syarat_termin_ids" :key="syarat.id" class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    {{ syarat.name }}
                    <button v-if="syarat.document" @click="openPdfViewer(syarat.id, syarat.name)" class="btn btn-sm btn-info ms-3">
                        <i class="fa fa-fw fa-eye"></i> View Document
                    </button>
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
    <PdfViewerModal :pdfUrl="currentPdfUrl" :show="showPdfModal" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import odooService from '@/services/odoo'
import PdfViewerModal from '@/components/PdfViewerModal.vue'

const route = useRoute()
const contract = ref(null)
const termins = ref([])
const payments = ref([])
const loading = ref(true)
const error = ref('')
const uploadError = ref('')

const currentPdfUrl = ref(null);
const showPdfModal = ref(false);

const ODOO_URL = import.meta.env.VITE_ODOO_URL;

const contractId = parseInt(route.params.id)

const fetchData = async () => {
  try {
    loading.value = true;
    // Fetch main contract details
    const contractData = await odooService.read('vit.kontrak', [contractId], 
      ['name', 'start_date', 'end_date', 'izin_prinsip_id', 'termin_ids', 'payment_ids', 'currency_id']);
    if (!contractData || contractData.length === 0) {
      throw new Error('Contract not found.');
    }
    contract.value = contractData[0];

    // Fetch termins and their syarat_termins
    if (contract.value.termin_ids.length > 0) {
        const terminData = contract.value.termin_ids

        termins.value = terminData;
    }

    // Fetch payments
    if (contract.value.payment_ids.length > 0) {
        payments.value = contract.value.payment_ids
    }

  } catch (err) {
    error.value = 'Failed to load contract details.';
    console.error(err);
  } finally {
    loading.value = false;
  }
}

const uploadDocument = async (syaratId, event) => {
    uploadError.value = ''; // Clear previous errors
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
                uploadError.value = 'File upload failed.';
            }
        } catch (err) {
            uploadError.value = 'An error occurred during upload.';
            console.error(err);
        }
    };
    reader.onerror = (error) => {
        uploadError.value = 'Error reading file.';
        console.error(error);
    };
}

const getDownloadUrl = (syaratId, syaratName) => {
    // Odoo's default URL for downloading binary field content
    return `${ODOO_URL}/web/content/vit.syarat_termin/${syaratId}/document?download=true&field=document&filename=${encodeURIComponent(syaratName)}`;
}

const openPdfViewer = (syaratId, syaratName) => {
  currentPdfUrl.value = getDownloadUrl(syaratId, syaratName);
  showPdfModal.value = true;
};

onMounted(fetchData);

</script>

<style scoped>
.accordion-button:not(.collapsed) {
    color: #0c63e4;
    background-color: #e7f1ff;
}
</style>