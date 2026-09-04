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
                  <div class="row g-3 align-items-end">
                    <div class="col-md-4 col-sm-12" v-if="contract.jenis_kontrak_id.type === 'fisik'">
                      <label for="syarat_progress" class="form-label">Syarat Progress (%)</label>
                      <input type="text" class="form-control" id="syarat_progress" :value="displayValue(termin.syarat_progress)" disabled>
                    </div>
                    <div class="col-md-4 col-sm-12" v-if="contract.jenis_kontrak_id.type === 'fisik'">
                      <label for="actual_progress" class="form-label">Actual Progress (%)</label>
                      <input type="text" class="form-control" id="actual_progress" v-model="termin.actual_progress" required="required" :disabled="termin.stage_id.display_name !== 'On Progress'">
                    </div>

                    <div class="col-12" v-if="contract.jenis_kontrak_id.type === 'non_fisik'">
                      <label for="syarat_output" class="form-label">Syarat Output (%)</label>
                      <input type="text" class="form-control" id="syarat_output" :value="displayValue(termin.syarat_output)" disabled>
                    </div>

                    <div class="col-12" v-if="contract.jenis_kontrak_id.type === 'non_fisik'">
                      <label for="actual_output" class="form-label">Actual Output (%)</label>
                      <input type="text" class="form-control" id="actual_output" v-model="termin.actual_output" required :disabled="termin.stage_id.display_name !== 'On Progress'">
                    </div>

                    <div class="col-12 d-flex justify-content-end">
                      <div class="form-label">&nbsp;</div>
                      <button class="form-control btn btn-primary progress-save-button" @click="updateProgress(termin.id)" :disabled="termin.stage_id.display_name !== 'On Progress'">Save</button>
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



                  <div class="syarat-status-ribbons">
                    <div v-if="syarat.upload_date && !syarat.verified" class="syarat-ribbon bg-warning">Uploaded</div>
                    <div v-if="syarat.upload_date && syarat.verified" class="syarat-ribbon bg-success">Verified</div>
                    <div v-if="syarat.upload_date && syarat.confirm" class="syarat-ribbon bg-primary">Confirmed</div>
                  </div>
                  <div class="px-1 fs-6">Due date: {{ displayValue(syarat.due_date) }}</div>
                  <form v-if="!syarat.upload_date" @submit.prevent="uploadDocument(syarat.id, $event)" class="d-flex mt-2">
                    <input type="file" class="form-control form-control-sm me-2" required :disabled="termin.stage_id.display_name !== 'On Progress'">
                    <button type="submit" class="btn btn-sm btn-secondary" :disabled="termin.stage_id.display_name !== 'On Progress'">Upload</button>
                  </form>
                </li>
                <li v-if="!termin.syarat_termin_ids.length" class="list-group-item">
                  <div class="px-1 fs-5">-</div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <h4 class="mt-4">Dokumen Kontrak</h4>
      <div class="card mt-4 mb-4">
        <div class="card-header">Dokumen Kontrak</div>
        <div class="card-body">
          <div v-if="contract.attachments.length" class="list-group">
            <div v-for="attachment in contract.attachments" :key="attachment.id" class="list-group-item position-relative contract-doc-item">
              <div class="px-1 fs-5">
                <a href="#" @click.prevent="openContractAttachment(attachment)">
                  {{ attachment.name }}
                  <i class="px-2 fa-regular fa-eye"></i>
                </a>
              </div>
              <div class="syarat-status-ribbons">
                <div class="syarat-ribbon bg-warning">Uploaded</div>
              </div>
              <div class="px-1 fs-6">Upload date: {{ displayValue(formatDate(attachment.create_date)) }}</div>
            </div>
          </div>
          <div v-else class="list-group-item">
            <div class="px-1 fs-5">-</div>
          </div>
        </div>
      </div>

      <h4 class="mt-4">Informasi Rekening Pembayaran</h4>
      <div class="card mt-4 mb-4">
        <div class="card-header">Data Rekening Vendor</div>
        <div class="card-body">
          <div ref="savedBankSelectRef" class="mb-3 saved-bank-select">
            <label class="form-label mb-2">Rekening Tersimpan</label>
            <div class="saved-bank-combobox">
              <input
                type="text"
                class="form-control saved-bank-search"
                :value="bankAccounts.length ? savedBankSearch : 'Belum ada'"
                :disabled="contract.stage_id.display_name !== 'On Progress' || !bankAccounts.length"
                placeholder="Pilih Rekening Tersimpan"
                autocomplete="off"
                @input="onSavedBankSearchInput"
                @focus="savedBankDropdownOpen = Boolean(bankAccounts.length)"
              >
              <button
                type="button"
                class="saved-bank-caret-button"
                :disabled="contract.stage_id.display_name !== 'On Progress' || !bankAccounts.length"
                @click="toggleSavedBankDropdown"
                title="Pilih rekening tersimpan"
              >
                v
              </button>
            </div>
            <div v-if="savedBankDropdownOpen" class="saved-bank-menu">
              <div v-if="!filteredBankAccounts.length" class="saved-bank-empty">Tidak ditemukan</div>
              <div v-for="bank in filteredBankAccounts" :key="bank.id" class="saved-bank-option">
                <button
                  type="button"
                  class="saved-bank-option-button"
                  @click="selectSavedBank(bank)"
                >
                  {{ displayValue(bank.bank_name) }} - {{ displayValue(bank.acc_number) }}
                </button>
                <button
                  type="button"
                  class="saved-bank-delete"
                  @click.stop="deleteSavedBank(bank)"
                  title="Hapus rekening"
                >
                  <i class="fa-regular fa-trash-can"></i>
                </button>
              </div>
            </div>
          </div>
          <div class="row g-3 align-items-end">
            <div class="col-md-5">
              <label for="nama_bank" class="form-label">Nama Bank</label>
              <input type="text" class="form-control" id="nama_bank" v-model="bankForm.bank_name" :disabled="contract.stage_id.display_name !== 'On Progress'" autocomplete="off">
            </div>
            <div class="col-md-5">
              <label for="nomor_rekening" class="form-label">Nomor Rekening</label>
              <input type="text" class="form-control" id="nomor_rekening" v-model="bankForm.acc_number" :disabled="contract.stage_id.display_name !== 'On Progress'" autocomplete="off">
            </div>
            <div class="col-md-2">
              <button class="form-control btn btn-primary" @click="updateBankInfo()" :disabled="contract.stage_id.display_name !== 'On Progress'">Simpan</button>
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
                    <th>Nama Bank</th>
                    <th>Nomor Rekening</th>
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
                    <td>{{ displayValue(payment.payment_bank_name) }}</td>
                    <td>{{ displayValue(payment.payment_bank_acc_number) }}</td>
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import odooService from '@/services/odoo'
import PdfViewerModal from '@/components/PdfViewerModal.vue'

const route = useRoute()
const contract = ref(null)
const termins = ref([])
const payments = ref([])
const bankAccounts = ref([])
const savedBankSelectRef = ref(null)
const savedBankDropdownOpen = ref(false)
const savedBankShowAll = ref(false)
const savedBankSearch = ref('')
const bankForm = ref({
  bank_name: '',
  acc_number: '',
})
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
      partner_bank_id:{
        fields:{display_name:{}}
      },
      payment_bank_name:{},
      payment_bank_acc_number:{},
      payment_bank_acc_holder:{},
      kanwil_id:{
        fields:{display_name:{}}
      },
      kanca_id:{
        fields:{display_name:{}}
      },
      attachments:{
        fields:{
          name:{},
          create_date:{},
          mimetype:{},
        }
      },
      termin_ids:{
        fields:{
          name:{},
          nilai:{},
          syarat_progress:{},
          actual_progress:{},
          syarat_output:{},
          actual_output:{},
          nama_bank:{},
          nomor_rekening:{},
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
              confirm:{},
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
          payment_bank_name:{},
          payment_bank_acc_number:{},
        }
      }
    }
    const contractData = await odooService.read('vit.kontrak', [contractId], specification);
    if (!contractData || contractData.length === 0) {
      throw new Error('Contract not found.');
    }
    contract.value = contractData[0];
    contract.value.attachments = contract.value.attachments || [];

    // Fetch termins and their syarat_termins
    if (contract.value.termin_ids.length > 0) {
        const terminData = contract.value.termin_ids.map(termin => ({
          ...termin,
          syarat_progress: inputValue(termin.syarat_progress),
          actual_progress: inputValue(termin.actual_progress),
          syarat_output: inputValue(termin.syarat_output),
          actual_output: inputValue(termin.actual_output),
          nama_bank: inputValue(termin.nama_bank),
          nomor_rekening: inputValue(termin.nomor_rekening),
          syarat_termin_ids: termin.syarat_termin_ids || [],
        }))
        termins.value = terminData;
    }

    // Fetch payments
    if (contract.value.payment_ids.length > 0) {
        payments.value = contract.value.payment_ids
    }
    await fetchBankInfo();

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

const getAttachmentUrl = (attachmentId, filename) => {
  return `${ODOO_URL}/web/content/${attachmentId}?download=false&filename=${encodeURIComponent(filename || 'document.pdf')}`;
}

const updateBankInfo = async () => {
  try {
    const existingInput = isExistingBankInput();
    const changedPaymentBank = isPaymentBankChanged();

    if (!existingInput && !confirm('Anda yakin ingin menyimpan rekening ini?')) {
      return;
    }

    const response = await odooService.callMethod('vit.kontrak', 'portal_payment_bank_save', [[contractId], payloadValue(bankForm.value.bank_name), payloadValue(bankForm.value.acc_number)], {}, { skipLoading: true });
    if (!response || response.error) {
      uploadError.value = `Gagal menyimpan. ${response?.error || response?.message || 'Terjadi kesalahan.'}`;
      console.error(response);
    } else {
      applyBankInfo(response);
      uploadError.value = null;
      if (existingInput && changedPaymentBank) {
        alert('Rekening pembayaran berhasil diperbarui.');
      }
    }
  } catch (err) {
    uploadError.value = `Terjadi error saat menyimpan. ${err}`;
    console.error(err);
  }
};

const fetchBankInfo = async () => {
  const response = await odooService.callMethod('vit.kontrak', 'portal_payment_bank_info', [[contractId]], {}, { skipLoading: true });
  if (response && !response.error) {
    applyBankInfo(response);
  }
};

const applyBankInfo = (data) => {
  bankAccounts.value = uniqueBankAccounts(data.bank_accounts || []);
  const selected = data.selected_bank || {};
  bankForm.value = {
    bank_name: inputValue(selected.bank_name),
    acc_number: inputValue(selected.acc_number),
  };
  savedBankSearch.value = selected.bank_name || selected.acc_number ? savedBankLabel(selected) : '';
  savedBankShowAll.value = false;
  if (contract.value) {
    contract.value.payment_bank_name = selected.bank_name || false;
    contract.value.payment_bank_acc_number = selected.acc_number || false;
    contract.value.payment_bank_acc_holder = selected.acc_holder || false;
  }
  if (termins.value.length > 0) {
    termins.value[0].nama_bank = inputValue(selected.bank_name);
    termins.value[0].nomor_rekening = inputValue(selected.acc_number);
  }
  payments.value = payments.value.map(payment => ({
    ...payment,
    payment_bank_name: selected.bank_name || false,
    payment_bank_acc_number: selected.acc_number || false,
  }));
};

const selectSavedBank = (bank) => {
  bankForm.value = {
    bank_name: inputValue(bank.bank_name),
    acc_number: inputValue(bank.acc_number),
  };
  savedBankSearch.value = savedBankLabel(bank);
  savedBankShowAll.value = false;
  savedBankDropdownOpen.value = false;
};

const onSavedBankSearchInput = (event) => {
  savedBankSearch.value = event.target.value;
  savedBankShowAll.value = false;
  savedBankDropdownOpen.value = true;
};

const toggleSavedBankDropdown = () => {
  savedBankShowAll.value = true;
  savedBankDropdownOpen.value = !savedBankDropdownOpen.value;
};

const closeSavedBankDropdownOnOutsideClick = (event) => {
  if (!savedBankSelectRef.value || savedBankSelectRef.value.contains(event.target)) {
    return;
  }
  savedBankDropdownOpen.value = false;
};

const deleteSavedBank = async (bank) => {
  const label = `${displayValue(bank.bank_name)} - ${displayValue(bank.acc_number)}`;
  if (!confirm(`Anda yakin ingin menghapus rekening ${label}?`)) {
    return;
  }

  const response = await odooService.callMethod('vit.kontrak', 'portal_payment_bank_delete', [[contractId], bank.id], {}, { skipLoading: true });
  if (!response || response.error) {
    uploadError.value = `Gagal menghapus rekening. ${response?.error || response?.message || 'Terjadi kesalahan.'}`;
    console.error(response);
    return;
  }
  response.bank_accounts = (response.bank_accounts || []).filter(account => account.id !== bank.id);
  if (response.selected_bank_id === bank.id) {
    response.selected_bank_id = false;
    response.selected_bank = false;
  }
  applyBankInfo(response);
  savedBankShowAll.value = false;
  savedBankDropdownOpen.value = false;
  uploadError.value = null;
};

const normalizeBankText = (value) => {
  return inputValue(value).trim().toLowerCase();
};

const normalizeAccountNumber = (value) => {
  return inputValue(value).trim();
};

const isExistingBankInput = () => {
  const bankName = normalizeBankText(bankForm.value.bank_name);
  const accountNumber = normalizeAccountNumber(bankForm.value.acc_number);
  if (!bankName || !accountNumber) {
    return false;
  }
  return bankAccounts.value.some((bank) => {
    return normalizeBankText(bank.bank_name) === bankName
      && normalizeAccountNumber(bank.acc_number) === accountNumber;
  });
};

const isPaymentBankChanged = () => {
  if (!contract.value) {
    return false;
  }
  return normalizeBankText(contract.value.payment_bank_name) !== normalizeBankText(bankForm.value.bank_name)
    || normalizeAccountNumber(contract.value.payment_bank_acc_number) !== normalizeAccountNumber(bankForm.value.acc_number);
};

const uniqueBankAccounts = (accounts) => {
  const seen = new Set();
  return accounts.filter((bank) => {
    const key = `${normalizeBankText(bank.bank_name)}|${normalizeAccountNumber(bank.acc_number)}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
};

const openPdfViewer = (syaratId, syaratName) => {
  currentPdfUrl.value = getDownloadUrl(syaratId, syaratName);
  showPdfModal.value = true;
};

const openContractAttachment = (attachment) => {
  currentPdfUrl.value = getAttachmentUrl(attachment.id, attachment.name);
  showPdfModal.value = true;
};

onMounted(() => {
  fetchData();
  document.addEventListener('click', closeSavedBankDropdownOnOutsideClick);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', closeSavedBankDropdownOnOutsideClick);
});

const isEmptyValue = (value) => {
  return value === false || value === null || value === undefined || value === ''
};

const displayValue = (value) => {
  return isEmptyValue(value) ? '-' : value;
};

const savedBankLabel = (bank) => {
  return `${displayValue(bank.bank_name)} - ${displayValue(bank.acc_number)}`;
};

const filteredBankAccounts = computed(() => {
  if (savedBankShowAll.value) {
    return bankAccounts.value;
  }
  const keyword = normalizeBankText(savedBankSearch.value);
  if (!keyword) {
    return bankAccounts.value;
  }
  return bankAccounts.value.filter((bank) => {
    return normalizeBankText(savedBankLabel(bank)).includes(keyword);
  });
});

const formatDate = (value) => {
  if (isEmptyValue(value)) return value;
  return String(value).split(' ')[0];
};

const inputValue = (value) => {
  return isEmptyValue(value) ? '' : value;
};

const payloadValue = (value) => {
  return isEmptyValue(value) ? false : value;
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

</script>

<style scoped>
.contract-doc-item {
  min-height: 84px;
}

.progress-save-button {
  max-width: 360px;
}

.saved-bank-select {
  max-width: 520px;
  position: relative;
}

.saved-bank-combobox {
  position: relative;
}

.saved-bank-search {
  padding-right: 40px;
}

.saved-bank-caret-button {
  align-items: center;
  background: transparent;
  border: 0;
  border-left: 1px solid #ced4da;
  color: #34516d;
  display: flex;
  justify-content: center;
  width: 38px;
  position: absolute;
  bottom: 1px;
  right: 1px;
  top: 1px;
}

.saved-bank-caret-button:disabled {
  color: #6c757d;
}

.saved-bank-menu {
  background-color: #fff;
  border: 1px solid #ced4da;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  left: 0;
  position: absolute;
  right: 0;
  top: calc(100% - 1px);
  z-index: 20;
}

.saved-bank-option {
  align-items: stretch;
  display: flex;
  min-height: 36px;
}

.saved-bank-option + .saved-bank-option {
  border-top: 1px solid #e5e9ef;
}

.saved-bank-empty {
  color: #6c757d;
  padding: 8px 12px;
}

.saved-bank-option-button {
  background: transparent;
  border: 0;
  color: #34516d;
  flex: 1;
  padding: 7px 12px;
  text-align: left;
}

.saved-bank-option-button:hover {
  background-color: #f4f7fb;
}

.saved-bank-delete {
  background: transparent;
  border: 0;
  border-left: 1px solid #ced4da;
  color: #b02a37;
  width: 38px;
}

.saved-bank-delete:hover {
  background-color: #f8d7da;
}
</style>
