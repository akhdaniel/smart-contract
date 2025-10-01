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
          <div class="d-flex justify-content-between">
            <div>
              <p><strong>Budget:</strong> {{ contract.budget_rkap_id.display_name }}</p>
              <p><strong>Izin Prinsip:</strong> {{ contract.izin_prinsip_id.display_name }}</p>
              <p><strong>Start Date:</strong> {{ contract.start_date }}</p>
              <p><strong>End Date:</strong> {{ contract.end_date }}</p>
              <p><strong>Stage:</strong> {{ contract.stage_id.display_name }}</p>
            </div>
            <div>
              <p><strong>Kanwil:</strong> {{ contract.partner_id.display_name }}</p>
              <p><strong>Kanca:</strong> {{ contract.partner_id.display_name }}</p>
              <p><strong>Nilai Kontrak:</strong> {{ contract.amount_kontrak }}</p>
              <p><strong>Jenis Kontrak:</strong> {{ contract.jenis_kontrak_id.display_name }}</p>
              <p><strong>Vendor:</strong> {{ contract.partner_id.display_name }}</p>
            </div>
          </div>
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
                    <div class="px-1 fs-5" v-if="!syarat.document" >
                      <div>{{ syarat.name }}</div>
                    </div>
                    <div class="px-1 fs-5" v-else >
                      <div>
                        <a class="" href="#" @click="openPdfViewer(syarat.id, syarat.name)">{{ syarat.name }}
                        <i class="px-2 fa-regular fa-eye"></i>
                        </a>
                        <i class="px-2 fa-regular fa-trash-can text-danger" @click="deleteDocument(syarat.id)" style="cursor: pointer;"></i>
                      </div>
                    </div>
                  </div>



                  <div v-if="syarat.document" class="syarat-ribbon bg-success">Verified</div>
                  <div class="px-1 fs-6">Due date: {{ syarat.due_date }}</div>
                  <form v-if="!syarat.document" @submit.prevent="uploadDocument(syarat.id, $event)" class="d-flex mt-2">
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
      amount_kontrak:{},
      jenis_kontrak_id:{
        fields:{display_name:{}}
      },
      budget_rkap_id:{
        fields:{display_name:{}}
      },
      stage_id:{
        fields:{display_name:{}}
      },
      izin_prinsip_id:{
        fields:{display_name:{}}
      },
      partner_id:{
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
              due_date:{},
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
    const specification = {
      name:{},
    }
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = async () => {
        const base64File = reader.result.split(',')[1];
        try {
            const success = await odooService.write('vit.syarat_termin', syaratId, { document: base64File }, specification);
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

const deleteDocument = async (syaratId) => {
  if (!confirm('Are you sure you want to delete this document?')) {
    return;
  }
  uploadError.value = ''; // Clear previous errors
  try {
    const success = await odooService.write('vit.syarat_termin', syaratId, { document: false });
    if (success) {
      // Find the specific syarat_termin and update its document property
      for (const termin of termins.value) {
        const targetSyarat = termin.syarat_termin_ids.find(s => s.id === syaratId);
        if (targetSyarat) {
          targetSyarat.document = false; // Update the document
          break;
        }
      }
    } else {
      uploadError.value = 'File deletion failed.';
    }
  } catch (err) {
    uploadError.value = 'An error occurred during deletion.';
    console.error(err);
  }
}


const getDownloadUrl = (syaratId, syaratName) => {
    // Odoo's default URL for downloading binary field content
    return `${ODOO_URL}/web/content/vit.syarat_termin/${syaratId}/document?field=document&filename=${encodeURIComponent(syaratName)}`;
}

const openPdfViewer = (syaratId, syaratName) => {
  currentPdfUrl.value = getDownloadUrl(syaratId, syaratName);
  showPdfModal.value = true;
};

// Format currency function
const formatCurrency = (amount) => {
  if (amount === null || amount === undefined) return 'Rp 0';
  try {
    // Convert to number if it's a string
    const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
    if (isNaN(numAmount)) return 'Rp 0';
    
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(numAmount);
  } catch (error) {
    console.error('Error formatting currency:', error);
    return 'Rp ' + amount;
  }
};

onMounted(fetchData);

</script>

<style scoped>
.accordion-button:not(.collapsed) {
    color: #0c63e4;
    background-color: #e7f1ff;
}

.accordion-button {
    color: #0c63e4;
    background-color: #eee;
}

</style>