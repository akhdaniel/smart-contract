# Vue Portal Deployment Guide

## Masalah yang Ditemukan
Progress update bekerja di local tapi tidak di server karena:
1. Environment variables berbeda
2. Data tidak di-refresh setelah update
3. Build/deploy process tidak benar

## Perbaikan yang Sudah Dibuat
- ✅ Tambah logging detail di `updateProgress`
- ✅ Auto refresh data setelah update berhasil
- ✅ Buat file `.env.production` untuk server
- ✅ Tambah validasi dan error handling

## Cara Deploy ke Server

### 1. Build Application
```bash
cd /mnt/disk2/odoo17/smc/vit-portal-vue
npm install
npm run build
```

### 2. Setup Environment Variables
Edit file `.env.production` di server:
```bash
VITE_ODOO_URL=https://your-odoo-server.com
VITE_ODOO_DB=your_production_database_name
```

### 3. Deploy Static Files
Copy file dari `dist/` ke folder static Odoo:
```bash
cp -r dist/* /path/to/odoo/addons/vit_portal/static/
```

### 4. Restart Odoo & Clear Cache
```bash
# Restart Odoo service
sudo systemctl restart odoo

# Clear browser cache (Ctrl+F5)
```

## Debug Steps
1. Buka Developer Tools (F12) → Console
2. Coba update progress
3. Check log messages:
   - "Updating progress for terminId: X"
   - "Sending filtered data: {actual_progress: Y}"
   - "Odoo write response: Z"
   - "Progress updated successfully, refreshing data..."

## Troubleshooting
- **Masih tidak update**: Check Odoo server logs
- **Environment salah**: Pastikan `.env.production` ada dan benar
- **Cache issue**: Hard refresh browser (Ctrl+F5)
- **Permission error**: Pastikan Odoo user bisa write ke static folder

## File yang Diubah
- `ContractDetail.vue`: Tambah logging & auto refresh
- `.env.production`: Environment untuk server
- `deploy.sh`: Script deployment (Linux only)