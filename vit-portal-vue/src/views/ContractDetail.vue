<template>
  <div>
    <div v-if="loading" class="d-flex justify-content-center mt-5">
      <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="contract">
      <h4>Kontrak: {{ contract.name }}</h4>

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
              <p><strong>Kanwil:</strong> {{ contract.kanwil_id.display_name }}</p>
              <p><strong>Kanca:</strong> {{ contract.kanca_id.display_name }}</p>
              <p><strong>Nilai Kontrak:</strong> {{ formatCurrency(contract.amount_kontrak) }}</p>
              <p><strong>Jenis Kontrak:</strong> {{ contract.jenis_kontrak_id.display_name }}</p>
              <p><strong>Vendor:</strong> {{ contract.partner_id.display_name }}</p>
            </div>
          </div>
        </div>
      </div>

      <h4 class="mt-4">Syarat Dokumen Penagihan</h4>
      <div v-if="uploadError" class="alert alert-danger mt-3">{{ uploadError }}</div>
      <div class="accordion mt-4" id="terminAccordion">
        <div v-for="(termin, index) in termins" :key="termin.id" class="accordion-item">
          <h2 class="accordion-header" :id="`heading${termin.id}`">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" :data-bs-target="`#collapse${termin.id}`" 
              :aria-expanded="index === 0 ? 'true' : 'false'" :aria-controls="`collapse${termin.id}`">
              {{ termin.master_nama_termin_id.display_name }}
            </button>
          </h2>
          <div :id="`collapse${termin.id}`" class="accordion-collapse collapse" :class="{ show: index === 0 }" 
            :aria-labelledby="`heading${termin.id}`" data-bs-parent="#terminAccordion">

            <div class="accordion-body">
              <div class="card">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start">
                    <div style="font-weight:bold">
                      {{ termin.persentase }}%
                      {{ formatCurrency(termin.nilai) }}
                    </div>
                    <div>{{ termin.name }}</div>
                    <div></div>
                    <div></div>
                    <div class="syarat-ribbon p-2" :class="{ 'bg-warning': termin.stage_id.display_name.toLowerCase() === 'draft', 'bg-success': termin.stage_id.display_name.toLowerCase() === 'on progress', 'bg-secondary': termin.stage_id.display_name.toLowerCase() === 'done' }">
                      {{ termin.stage_id.display_name }}
                    </div>
                </div>
             
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-4 col-sm-12" v-if="contract.jenis_kontrak_id.type === 'fisik'">
                      <label for="syarat_progress" class="form-label">Syarat Progress (%)</label>
                      <input type="text" class="form-control" id="syarat_progress" v-model="termin.syarat_progress" disabled>
                    </div>
                    <div class="col-md-4 col-sm-12" v-if="contract.jenis_kontrak_id.type === 'fisik'">
                      <label for="actual_progress" class="form-label">Actual Progress (%)</label>
                      <input type="text" class="form-control" id="actual_progress" v-model="termin.actual_progress" required="required" :disabled="termin.stage_id.display_name !== 'On Progress'">
                    </div>

                    <div v-if="contract.jenis_kontrak_id.type === 'non_fisik'">
                      <label for="syarat_output" class="form-label">Syarat Output (%)</label>
                      <input type="text" class="form-control" id="syarat_progress" v-model="termin.syarat_output" disabled>
                    </div>

                    <div v-if="contract.jenis_kontrak_id.type === 'non_fisik'">
                      <label for="actual_output" class="form-label">Actual Output (%)</label>
                      <input type="text" class="form-control" id="actual_progress" v-model="termin.actual_output" required :disabled="termin.stage_id.display_name !== 'On Progress'">
                    </div>

                    <div class="col-md-4 col-sm-12">
                      <div class="form-label">&nbsp;</div>
                      <button class="form-control btn btn-primary" @click="updateProgress(termin.id)" :disabled="termin.stage_id.display_name !== 'On Progress'">Save</button>
                    </div>   

                  </div>          
                </div>
                </div>
              </div>
            </div>

            <div class="accordion-body">
              <h6>Syarat Penagihan</h6>
              <ul class="list-group">
                <li v-for="syarat in termin.syarat_termin_ids" :key="syarat.id" class="list-group-item position-relative">
                  <div class="d-flex justify-content-between align-items-start">
                    <div class="px-1 fs-5" v-if="!syarat.upload_date" >
                      <div>{{ syarat.name }}</div>
                    </div>
                    <div class="px-1 fs-5" v-else >
                      <div>
                        <a class="" href="#" @click="openPdfViewer(syarat.id, syarat.name)">{{ syarat.name }}
                        <i class="px-2 fa-regular fa-eye"></i>
                        </a>
                        <i v-if="syarat.upload_date && !syarat.verified" class="px-2 fa-regular fa-trash-can text-danger" @click="deleteDocument(syarat.id)" style="cursor: pointer;"></i>
                      </div>
                    </div>
                  </div>



                  <div v-if="syarat.upload_date && !syarat.verified" class="syarat-ribbon bg-warning">Uploaded</div>
                  <div v-if="syarat.upload_date && syarat.verified" class="syarat-ribbon bg-success">Verified</div>
                  <div class="px-1 fs-6">Due date: {{ syarat.due_date }}</div>
                  <form v-if="!syarat.upload_date" @submit.prevent="uploadDocument(syarat.id, $event)" class="d-flex mt-2">
                    <input type="file" class="form-control form-control-sm me-2" required :disabled="termin.stage_id.display_name !== 'On Progress'">
                    <button type="submit" class="btn btn-sm btn-secondary" :disabled="termin.stage_id.display_name !== 'On Progress'">Upload</button>
                  </form>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <h4 class="mt-4">Status Pembayaran</h4>
      <div class="card mt-4 mb-4">
        <div class="card-header">Daftar Pembayaran dan history status pembayaran</div>
        <div class="card-body">
          <table class="table table-striped mt-3">
            <thead>
                <tr>
                    <th>Number</th>
                    <th>Termin</th>
                    <th>Request Date</th>
                    <th>Payment Date</th>
                    <th class="text-end">Amount</th>
                    <th class="text-center">Status</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="payment in payments" :key="payment.id">
                    <td>{{ payment.name }}</td>
                    <td>{{ payment.termin_id.master_nama_termin_id.display_name }}</td>
                    <td>{{ payment.request_date?payment.request_date:"" }}</td>
                    <td>{{ payment.payment_date }}</td>
                    <td class="text-end">{{ formatCurrency(payment.amount) }}</td>
                    <td class="text-center">
                      
                      <span class="badge" :class="{
                        'bg-info': payment.stage_id.display_name === 'On Progress',
                        'bg-secondary': payment.stage_id.display_name === 'Draft',
                        'bg-success': payment.stage_id.display_name === 'Done'
                      }">
                        {{ payment.stage_id.display_name }}
                      </span>

                    </td>
                </tr>
            </tbody>
          </table>
        </div>
      </div>
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
        fields:{display_name:{}, type:{}}
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
      kanwil_id:{
        fields:{display_name:{}}
      },
      kanca_id:{
        fields:{display_name:{}}
      },
      termin_ids:{
        fields:{
          name:{},
          nilai:{},
          syarat_progress:{},
          actual_progress:{},
          syarat_output:{},
          actual_output:{},
          master_nama_termin_id:{
            fields:{
              display_name:{}
            }
          },
          persentase:{},
          stage_id:{fields:{display_name:{}}},
          syarat_termin_ids:{
            fields:{
              name:{},
              due_date:{},
              // document:{},
              verified:{},
              upload_date:{},
            }
          },
        }
      },
      budget_rkap_id:{
        fields:{display_name:{}}
      },
      payment_ids:{
        fields:{
          name:{},
          request_date:{},
          payment_date:{},
          amount:{},
          termin_id:{
            fields:{
              display_name:{},
              master_nama_termin_id:{
                fields:{display_name:{}}
              },
            }
          },
          stage_id:{
            fields:{
              display_name:{}, 
            }
          },
        }
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
      upload_date:{}
    }
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = async () => {
        const base64File = reader.result.split(',')[1];
        try {
            const success = await odooService.write('vit.syarat_termin', syaratId, { 
              document: base64File, 
              upload_date: new Date() }, 
            specification);
            if (success) {
                // Find the specific syarat_termin and update its document property
                for (const termin of termins.value) {
                    let targetSyarat = termin.syarat_termin_ids.find(s => s.id === syaratId);
                    if (targetSyarat) {
                        targetSyarat.upload_date = new Date(); // date Update the document
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
  const specification = {
      name:{},
      upload_date:{}
    }
  uploadError.value = ''; // Clear previous errors
  try {
    const success = await odooService.write('vit.syarat_termin', syaratId, { document: false , upload_date:false}, specification);
    if (success) {
      // Find the specific syarat_termin and update its document property
      for (const termin of termins.value) {
        const targetSyarat = termin.syarat_termin_ids.find(s => s.id === syaratId);
        if (targetSyarat) {
          targetSyarat.upload_date = false; // Update the document
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

const updateProgress = async (terminId) =>{
  console.log('terminId',terminId)
  const targetTermin = termins.value.find(s => s.id === terminId);
  console.log(contract.value.jenis_kontrak_id.type)
  if (contract.value.jenis_kontrak_id.type=='fisik'){
    if (targetTermin.syarat_progress<100){ // termin 1,2...
      if (targetTermin.actual_progress <= targetTermin.syarat_progress) 
      {
        alert('Untuk jenis kontrak Fisik, actual progres harus lebih besar dari syarat progress penagihan.')
      }
    }
    else // termin terakhir
    {
      if (targetTermin.actual_progress != 100) 
      {
        alert('Untuk jenis kontrak Fisik, actual progres termin terakhir harus 100%.')
      }      
    }

  }

  try {
    const keysToKeep = ["actual_progress", "actual_output"];
    const filtered = Object.keys(targetTermin)
      .filter(key => keysToKeep.includes(key))
      .reduce((acc, key) => ({ ...acc, [key]: targetTermin[key] }), {});
    console.log(filtered); 

    const specification = {
      name:{},
      actual_progress:{},
      actual_output:{}
    }  
    const response = await odooService.write('vit.termin', terminId, filtered, specification);
    console.log(response)
    if (response.error){
      uploadError.value = `An error occurred during update. ${response.message}`;
      console.error(response);
    }
    else{
      uploadError.value = null
    }
  } catch (err) {
      uploadError.value = `An error occurred during update. ${err}`;
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

onMounted(fetchData);

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

</script>
