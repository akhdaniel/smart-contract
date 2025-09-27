<template>
  <div class="modal fade" id="pdfViewerModal" tabindex="-1" aria-labelledby="pdfViewerModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="pdfViewerModalLabel">View Document</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div v-if="pdfUrl" class="embed-responsive embed-responsive-16by9" style="height: 70vh;">
            <iframe :src="pdfUrl" width="100%" height="100%" frameborder="0"></iframe>
          </div>
          <div v-else class="alert alert-info">No document to display.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, watch, onMounted, ref, defineEmits } from 'vue';
import { Modal } from 'bootstrap';

const props = defineProps({
  pdfUrl: {
    type: String,
    default: null,
  },
  show: {
    type: Boolean,
    default: false,
  }
});

const emit = defineEmits(['update:show']);

const modalInstance = ref(null);

onMounted(() => {
  const modalElement = document.getElementById('pdfViewerModal');
  modalInstance.value = new Modal(modalElement);

  modalElement.addEventListener('hidden.bs.modal', () => {
    emit('update:show', false);
  });
});

watch(() => props.show, (newVal) => {
  if (newVal) {
    modalInstance.value.show();
  } else {
    modalInstance.value.hide();
  }
});
</script>

<style scoped>
/* Add any specific styles for your modal here */
</style>
