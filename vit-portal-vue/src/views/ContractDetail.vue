<template>
  <div>
    <div v-if="loading" class="d-flex justify-content-center mt-5">
      <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="contract">
      <h3>Kontrak: {{ contract.name }}</h3>

      <div class="card mt-4">
        <div class="card-header">Detail Kontrak</div>
        <div class="card-body">
            <p><strong>Budget:</strong> {{ contract.budget_rkap_id.display_name }}</p>
            <p><strong>Izin Prinsip:</strong> {{ contract.izin_prinsip_id.display_name }}</p>
            <p><strong>Start Date:</strong> {{ contract.start_date }}</p>
            <p><strong>End Date:</strong> {{ contract.end_date }}</p>
        </div>
      </div>

      <h4 class="mt-5">Syarat Dokumen Penagihan</h4>
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
                <li v-for="syarat in termin.syarat_termin_ids" :key="syarat.id" class="list-group-item position-relative">
                  <div class="d-flex justify-content-between align-items-start">
                    <div class="fw-bold fs-5">
                      {{ syarat.name }}
                    </div>
                    <div v-if="syarat.document" class="syarat-ribbon bg-success p-2">Completed</div>
                  </div>
                  <div v-if="syarat.document" class="mt-2">
                    <button @click="openPdfViewer(syarat.id, syarat.name)" class="btn btn-sm btn-info">
                        <i class="fa fa-fw fa-eye"></i> View Document
                    </button>
                  </div>
                  <form v-else @submit.prevent="uploadDocument(syarat.id, $event)" class="d-flex mt-2">
                    <input type="file" class="form-control form-control-sm me-2" required>
                    <button type="submit" class="btn btn-sm btn-primary">Upload</button>
                  </form>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <h4 class="mt-5">Status Pembayaran</h4>
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
    <PdfViewerModal :pdfUrl="currentPdfUrl" :show="showPdfModal" @update:show="showPdfModal = $event" />
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
    // const fieldsString = 'name,start_date,end_date,izin_prinsip_id,termin_ids[name,master_nama_termin_id,persentase,syarat_termin_ids[name,document]],payment_ids[name,budget_rkap_id]';
    const specification = {
      name:{},
      start_date:{},
      end_date:{},
      budget_rkap_id:{
        fields:{display_name:{}}
      },
      izin_prinsip_id:{
        fields:{display_name:{}}
      },
      termin_ids:{
        fields:{
          name:{},
          master_nama_termin_id:{
            fields:{
              display_name:{}
            }
          },
          persentase:{},
          syarat_termin_ids:{
            fields:{
              name:{},
              document:{}
            }
          },
        }
      },
      budget_rkap_id:{
        fields:{display_name:{}}
      },
      payment_ids:{
        name:{},
        amount:{}
      }
    }
    const contractData = await odooService.read('vit.kontrak', [contractId], specification);
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
                // Find the specific syarat_termin and update its document property
                for (const termin of termins.value) {
                    const targetSyarat = termin.syarat_termin_ids.find(s => s.id === syaratId);
                    if (targetSyarat) {
                        targetSyarat.document = base64File; // Update the document
                        break;
                    }
                }
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
    return `${ODOO_URL}/web/content/vit.syarat_termin/${syaratId}/document?field=document&filename=${encodeURIComponent(syaratName)}`;
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
.accordion-button {
    color: #0c63e4;
    background-color: #eee;
}
.bg-success {
  background-color: rgb(7, 185, 102) !important
}
.btn-info{
  color: #fff;
}
</style>