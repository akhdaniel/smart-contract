#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import io
import base64


try:
    import openpyxl
    from openpyxl import load_workbook
except ImportError:
    openpyxl = None


class WizardImportKompleksPergudangan(models.TransientModel):
    _name = "wizard.import.kompleks.pergudangan"
    _description = "Wizard Import Kompleks Pergudangan dari Excel"

    file_data = fields.Binary(string="File Excel", required=True)
    file_name = fields.Char(string="File Name")

    @api.model
    def create(self, vals):
        if not openpyxl:
            raise UserError(_("Library openpyxl tidak terinstall. Mohon install library openpyxl."))
        return super(WizardImportKompleksPergudangan, self).create(vals)

    def action_import_excel(self):
        """
        Import data Kompleks Pergudangan dari file Excel
        """
        if not self.file_data:
            raise UserError(_("Silakan pilih file Excel terlebih dahulu."))

        try:
            # Decode file data
            file_data = base64.b64decode(self.file_data)
            
            # Load workbook dengan data_only=True untuk read nilai bukan formula
            workbook = load_workbook(io.BytesIO(file_data), data_only=True)
            # Process all worksheets: detect header per sheet and import rows
            imported_count = 0
            created_ids = []
            errors = []
            counts_by_sheet = {}

            def _get_headers_from_row(sheet_obj, row_idx):
                headers_local = []
                for cell in sheet_obj[row_idx]:
                    val = cell.value
                    if val is None:
                        headers_local.append('')
                        continue
                    h = str(val).strip()
                    h = ' '.join(h.split())
                    headers_local.append(h)
                return headers_local

            def _find_header_row(sheet_obj, max_search=30):
                for r in range(1, max_search + 1):
                    row = list(sheet_obj.iter_rows(min_row=r, max_row=r, values_only=True))[0]
                    row_str = ' '.join([str(x) for x in row if x is not None]).lower()
                    if 'tempat' in row_str and 'kedudukan' in row_str:
                        return r
                    if 'kompleks' in row_str and 'pergudangan' in row_str:
                        return r
                return None

            # process every worksheet in the workbook
            for sheet in workbook.worksheets:
                sheet_count = 0
                try:
                    header_row_idx = _find_header_row(sheet, max_search=40)
                    if header_row_idx is None:
                        # fallback to first non-empty row
                        header_row_idx = 1

                    headers = _get_headers_from_row(sheet, header_row_idx)
                    # if the primary columns cannot be found later we will record an error

                    # Find columns
                    tempat_col = None
                    kompleks_col = None
                    kanwil_col = None
                    col_c = None
                    col_d = None
                    for idx, h in enumerate(headers):
                        key = (h or '').lower()
                        if 'tempat' in key or 'kedudukan' in key or 'kanca' in key:
                            if tempat_col is None:
                                tempat_col = idx
                        if 'kompleks' in key or 'pergudangan' in key or 'kompleks pergudangan' in key:
                            if kompleks_col is None:
                                kompleks_col = idx
                        if 'kanwil' in key:
                            if kanwil_col is None:
                                kanwil_col = idx
                    
                    # Also get columns C (index 2) and D (index 3) for additional kanca info
                    if len(headers) > 2:
                        col_c = 2
                    if len(headers) > 3:
                        col_d = 3

                    if tempat_col is None or kompleks_col is None:
                        # skip sheet if required columns not found
                        errors.append(f"Sheet '{sheet.title}' header tidak mengandung kolom 'tempat'/'kompleks'; baris header={header_row_idx}, headers={headers}")
                        continue

                    # detect if kompleks_col points to numbering column; shift if needed
                    def _col_stats_local(sheet_obj, col_idx, header_row_idx, max_rows=12):
                        text_count = 0
                        num_count = 0
                        blank_count = 0
                        for r_off in range(1, max_rows + 1):
                            row_num = header_row_idx + r_off
                            try:
                                cell_val = sheet_obj.cell(row=row_num, column=col_idx + 1).value
                            except Exception:
                                cell_val = None
                            if cell_val is None or (isinstance(cell_val, str) and str(cell_val).strip() == ''):
                                blank_count += 1
                            elif isinstance(cell_val, (int, float)):
                                num_count += 1
                            else:
                                s = str(cell_val).strip()
                                if s.replace('.', '').isdigit():
                                    num_count += 1
                                else:
                                    text_count += 1
                        return text_count, num_count, blank_count

                    k_text, k_num, k_blank = _col_stats_local(sheet, kompleks_col, header_row_idx)
                    next_idx = kompleks_col + 1
                    n_text, n_num, n_blank = (0, 0, 0)
                    if next_idx < len(headers):
                        n_text, n_num, n_blank = _col_stats_local(sheet, next_idx, header_row_idx)
                    # If kompleks_col has mostly numbers (like 1., 2., 3.), shift to next column which should have the actual name
                    if k_num > k_text and n_text > n_num and next_idx < len(headers):
                        kompleks_col = next_idx

                    # iterate data rows
                    current_tempat = None
                    for row_idx, row in enumerate(sheet.iter_rows(min_row=header_row_idx + 1, values_only=True), start=header_row_idx + 1):
                        try:
                            row_list = list(row) if row is not None else []
                            if not any([cell for cell in row_list if cell not in (None, '')]):
                                continue

                            tempat_val = None
                            kompleks_val = None

                            if tempat_col < len(row_list):
                                val = row_list[tempat_col]
                                if val not in (None, ''):
                                    tempat_val = str(val).strip()
                                    current_tempat = tempat_val
                                else:
                                    tempat_val = current_tempat

                            if kompleks_col < len(row_list):
                                val = row_list[kompleks_col]
                                if val not in (None, ''):
                                    kompleks_val = str(val).strip()
                            # if the value looks like a numbering and the next column exists with text, shift
                            import re
                            if kompleks_val and re.match(r'^\d+([a-z])?\.?$', kompleks_val, re.I):
                                # check next column
                                shift_idx = kompleks_col + 1
                                if shift_idx < len(row_list):
                                    next_val = row_list[shift_idx]
                                    if next_val not in (None, ''):
                                        next_str = str(next_val).strip()
                                        # if next column is non-numeric text, use it as kompleks
                                        if not re.match(r'^\d+([a-z])?\.?$', next_str, re.I):
                                            kompleks_val = next_str
                                            # update header column for future rows
                                            kompleks_col = shift_idx

                            if not kompleks_val:
                                continue

                            # skip rows where kompleks value is just a number (total rows or stray counts)
                            if re.match(r'^\d+(?:\.\d+)?$', kompleks_val.strip()):
                                # e.g. the bottom "18" or "11" total count – not a real name
                                continue
                            # also skip any row that contains the word "total" anywhere
                            if any(isinstance(c, str) and 'total' in c.lower() for c in row_list):
                                continue

                            # heuristic to skip address/detail rows
                            # Check jika ada nomor di kolom sebelum kompleks atau di kolom C (index 2)
                            numbering_col = kompleks_col - 1
                            is_numbering = False
                            
                            # First check kolom sebelum kompleks_col
                            if numbering_col is not None and numbering_col >= 0 and numbering_col < len(row_list):
                                left_val = row_list[numbering_col]
                                if left_val not in (None, ''):
                                    if isinstance(left_val, (int, float)):
                                        is_numbering = True
                                    else:
                                        sleft = str(left_val).strip()
                                        # Check if it's a number, or number + letter (like 3a, 1b, 3a.) or number + dash (like 3 -)
                                        import re
                                        if re.match(r'^\d+([a-z])?\.?$', sleft, re.I) or re.match(r'^\d+\s*[-–]', sleft):
                                            is_numbering = True
                            
                            # Jika tidak ketemu di kolom sebelum, coba cek kolom C (index 2)
                            if not is_numbering and col_c is not None and col_c < len(row_list):
                                col_c_val = row_list[col_c]
                                if col_c_val not in (None, ''):
                                    if isinstance(col_c_val, (int, float)):
                                        is_numbering = True
                                    else:
                                        sc = str(col_c_val).strip()
                                        import re
                                        if re.match(r'^\d+([a-z])?\.?$', sc, re.I):
                                            is_numbering = True
                            if not is_numbering:
                                # we only relied on numbering to distinguish data rows from address lines;
                                # if there's no numbering we should still consider importing the row unless
                                # it looks like a pure address/detail line (e.g. contains street/kel/kab labels)
                                address_tokens = ['jl', 'jalan', 'ds.', 'ds', 'kec', 'kab', 'kel', 'kota']
                                found_addr = False
                                for c in row_list:
                                    if isinstance(c, str):
                                        low = c.lower().strip()
                                        for tok in address_tokens:
                                            if low.startswith(tok):
                                                found_addr = True
                                                break
                                    if found_addr:
                                        break
                                if found_addr:
                                    continue
                                # otherwise treat as valid data row

                            kompleks_vals = {
                                'name': kompleks_val,
                            }
                            # prepare lists for many2many relationships
                            kanca_ids = []
                            kanwil_ids = []

                            # Assign kanca based on 'tempat' (tempat_val or current_tempat)
                            try:
                                kanca_name = tempat_val or current_tempat
                                if kanca_name:
                                    kanca_try = str(kanca_name).strip()
                                    # split if multiple names present (comma, semicolon, slash)
                                    import re
                                    parts = re.split(r'[;,/]\s*', kanca_try)
                                    for part in parts:
                                        part = part.strip()
                                        if not part:
                                            continue
                                        kanca = self.env['vit.kanca'].sudo().search([('name', 'ilike', part)], limit=1)
                                        if not kanca:
                                            simple = part.split(',')[0].split('-')[0].strip()
                                            if simple and simple != part:
                                                kanca = self.env['vit.kanca'].sudo().search([('name', 'ilike', simple)], limit=1)
                                        # if still not found, auto-create kanca
                                        if not kanca:
                                            base = simple or part
                                            base = base.strip()
                                            if base:
                                                if base.lower().startswith('kanca'):
                                                    new_name = base
                                                else:
                                                    new_name = 'Kanca ' + ' '.join([w.capitalize() for w in base.split()])
                                                kanca_exist = self.env['vit.kanca'].sudo().search([('name', '=', new_name)], limit=1)
                                                if not kanca_exist:
                                                    try:
                                                        kanca = self.env['vit.kanca'].sudo().create({'name': new_name})
                                                    except Exception:
                                                        kanca = None
                                                else:
                                                    kanca = kanca_exist
                                        if kanca:
                                            kanca_ids.append(kanca.id)
                                            # collect kanwil(s) from kanca if defined
                                            if hasattr(kanca, 'kanwil_id') and kanca.kanwil_id:
                                                if hasattr(kanca.kanwil_id, 'ids'):
                                                    kanwil_ids += kanca.kanwil_id.ids
                                                else:
                                                    kanwil_ids.append(kanca.kanwil_id.id)
                            except Exception:
                                pass

                            # read explicit kanwil column if available
                            if kanwil_col is not None and kanwil_col < len(row_list):
                                val = row_list[kanwil_col]
                                if val not in (None, ''):
                                    kanwil_text = str(val).strip()
                                    parts = re.split(r'[;,/]\s*', kanwil_text)
                                    for part in parts:
                                        part = part.strip()
                                        if not part:
                                            continue
                                        kw = self.env['vit.kanwil'].sudo().search([('name', 'ilike', part)], limit=1)
                                        if not kw:
                                            try:
                                                kw = self.env['vit.kanwil'].sudo().create({'name': part})
                                            except Exception:
                                                kw = None
                                        if kw:
                                            kanwil_ids.append(kw.id)

                            if kanca_ids:
                                kompleks_vals['kanca_id'] = [(6, 0, list(set(kanca_ids)))]
                            if kanwil_ids:
                                kompleks_vals['kanwil_id'] = [(6, 0, list(set(kanwil_ids)))]
                            kompleks_pergudangan = self.env['vit.kompleks_pergudangan'].sudo().create(kompleks_vals)
                            created_ids.append(kompleks_pergudangan.id)
                            imported_count += 1
                            sheet_count += 1
                        except Exception as e:
                            errors.append(f"Sheet '{sheet.title}' Baris {row_idx}: {str(e)}")
                except Exception:
                    # ignore sheet-level errors and continue with others
                    continue
                finally:
                    # record how many rows imported from this sheet
                    if sheet_count:
                        counts_by_sheet[sheet.title] = sheet_count
                    else:
                        # no rows imported, warn the user
                        errors.append(f"Sheet '{sheet.title}' tidak ada baris data yang valid.")
            
            # If we created records, open a list view showing them
            if imported_count > 0:
                action = {
                    'type': 'ir.actions.act_window',
                    'name': _('Imported Kompleks Pergudangan'),
                    'res_model': 'vit.kompleks_pergudangan',
                    'view_mode': 'tree,form',
                    'domain': [('id', 'in', created_ids)],
                    'context': dict(self.env.context, active_test=False),
                }
                return action

            # Show result
            if imported_count > 0:
                message = f"Berhasil import {imported_count} Kompleks Pergudangan"
                if counts_by_sheet:
                    details = []
                    for name, cnt in counts_by_sheet.items():
                        details.append(f"{name}: {cnt}")
                    message += " (" + ", ".join(details) + ")"
            else:
                message = "Tidak ada data yang diimport."
            if errors:
                message += f"\n\nError:\n" + "\n".join(errors[:10])
                if len(errors) > 10:
                    message += f"\n... dan {len(errors) - 10} error lainnya"

            raise UserError(_(message))
            
        except UserError:
            raise
        except Exception as e:
            raise UserError(_("Error saat membaca file Excel: %s") % str(e))
