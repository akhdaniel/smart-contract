# -*- coding: utf-8 -*-

from odoo import models, api
import logging
_logger = logging.getLogger(__name__)
from .tools import domain_to_sql, process_domain

class BudgetRkap(models.Model):
    _inherit = 'vit.budget_rkap'

    @api.model
    def get_statistics(self, domain=None, field=None, limit=10, offset=0):
        """
        This method is used to get the statistics of the budgets.
        Sekarang kanwil_id diambil dari izin_prinsip (bukan dari budget_rkap langsung).
        """
        domain = domain or []
        _logger.info("📊 DASHBOARD DOMAIN MASUK: %s", domain)

        domain_ip = []
        # collect budget_date filters (range) to apply when searching budget_rkap
        budget_date_domain = []
        for cond in domain:
            if cond[0] == 'kanwil_id':
                domain_ip.append(('kanwil_id', '=', cond[2]))
            elif cond[0] == 'budget_date' or cond[0] == 'year':
                # keep budget_date related conditions to apply later to budgets search
                budget_date_domain.append(cond)
            else:
                domain_ip.append(cond)

        if not domain_ip:
            record = self.env['vit.izin_prinsip'].search([], limit=1)
            if record and record.kanwil_id:
                domain_ip = [('kanwil_id', '=', record.kanwil_id.id)]

        # if field == 'total_budget_realisasi':
        #     izin_prinsip_list = self.env['vit.izin_prinsip'].search(domain_ip)

        #     record = izin_prinsip_list[:1]

        #     master_ids = izin_prinsip_list.mapped('master_budget_id').ids

        #     budgets_domain = [('master_budget_id', 'in', master_ids)] + budget_date_domain
        #     budgets = self.env['vit.budget_rkap'].search(budgets_domain)

        #     amount = sum(budgets.mapped('amount'))
        #     total_realisasi = sum(budgets.mapped('total_amount_payment'))

        #     return {
        #         'kanwil_name': record.kanwil_id.name if record else '',
        #         'amount': amount,
        #         'amount_formatted': "{:,.0f}".format(amount).replace(",", "."),
        #         'total_realisasi': total_realisasi,
        #         'total_realisasi_formatted': "{:,.0f}".format(total_realisasi).replace(",", "."),
        #     }

        if field == 'total_budget_realisasi':
            izin_prinsip_list = self.env['vit.izin_prinsip'].search(domain_ip)
            record = izin_prinsip_list[:1]
            kanwil_id = record.kanwil_id.id if record else False

            master_ids = izin_prinsip_list.mapped('master_budget_id').ids

            if budget_date_domain:
                allowed_master_ids = master_ids
                if allowed_master_ids:
                    izin_filtered_for_year = izin_prinsip_list.filtered(
                        lambda ip: ip.master_budget_id
                        and ip.master_budget_id.id in allowed_master_ids
                        and ip.kanwil_id.id == kanwil_id
                    )
                    total_pagu = sum(izin_filtered_for_year.mapped('total_pagu'))
                else:
                    total_pagu = 0
            else:
                izin_filtered = izin_prinsip_list.filtered(lambda ip: ip.kanwil_id.id == kanwil_id)
                total_pagu = sum(izin_filtered.mapped('total_pagu'))

            budgets_domain = [('master_budget_id', 'in', master_ids)] + budget_date_domain
            budgets = self.env['vit.budget_rkap'].search(budgets_domain)

            total_realisasi = 0
            for b in budgets:
                payments = self.env['vit.payment'].search([
                    ('budget_rkap_id', '=', b.id),
                    ('kanwil_id', '=', kanwil_id),
                    ('stage_is_done', '=', True),
                ])
                total_realisasi += sum(payments.mapped('amount'))

            return {
                'kanwil_name': record.kanwil_id.name if record else '',
                'amount': total_pagu,
                'amount_formatted': "{:,.0f}".format(total_pagu).replace(",", "."),
                'total_realisasi': total_realisasi,
                'total_realisasi_formatted': "{:,.0f}".format(total_realisasi).replace(",", "."),
            }









        # if field == 'persentase_tl_droping':
        #     izin_prinsip_list = self.env['vit.izin_prinsip'].search(domain_ip)
        #     record = izin_prinsip_list[:1]
        #     master_ids = izin_prinsip_list.mapped('master_budget_id').ids
        #     kanwil_id = record.kanwil_id.id if record else False

        #     budgets_domain = [('master_budget_id', 'in', master_ids)] + budget_date_domain
        #     budgets = self.env['vit.budget_rkap'].search(budgets_domain)

        #     amount = sum(budgets.mapped('amount'))
        #     total_realisasi = sum(budgets.mapped('total_amount_payment'))

        #     droping_domain = [('master_budget_id', 'in', master_ids)]
        #     if kanwil_id:
        #         droping_domain.append(('kanwil_id', '=', kanwil_id))

        #     droping_filtered = self.env['vit.droping'].search(droping_domain)
        #     total_droping = sum(droping_filtered.mapped('jumlah'))

        #     persentasi_tl = (total_realisasi / amount * 100) if amount > 0 else 0
        #     persentasi_droping = (total_realisasi / total_droping * 100) if total_droping > 0 else 0

        #     return {
        #         'persentasi_tl': round(persentasi_tl, 2),
        #         'persentasi_droping': round(persentasi_droping, 2),
        #     }


        if field == 'persentase_tl_droping':
            izin_prinsip_list = self.env['vit.izin_prinsip'].search(domain_ip)
            record = izin_prinsip_list[:1]
            kanwil_id = record.kanwil_id.id if record else False

            # Ambil semua master budget dari izin prinsip
            master_ids = izin_prinsip_list.mapped('master_budget_id').ids

            # Ambil semua budget RKAP yang terkait
            budgets_domain = [('master_budget_id', 'in', master_ids)] + budget_date_domain
            budgets = self.env['vit.budget_rkap'].search(budgets_domain)

            # --- Hitung total qty izin prinsip & kontrak (SEMUA master_budget) ---
            total_qty_izin_prinsip = sum(budgets.mapped('total_qty_izin_prinsip'))
            total_qty_kontrak = sum(budgets.mapped('total_qty_kontrak'))

            # --- Hitung total droping (SEMUA master_budget) ---
            droping_domain = [('master_budget_id', 'in', master_ids)]
            if kanwil_id:
                droping_domain.append(('kanwil_id', '=', kanwil_id))
            droping_filtered = self.env['vit.droping'].search(droping_domain)
            total_droping = sum(droping_filtered.mapped('jumlah'))

            # --- Hitung total_pagu & previous_remaining GLOBAL (bukan per master) ---
            total_pagu = sum(budgets.mapped('total_pagu_izin_prinsip'))
            total_remaining = sum(budgets.mapped('previous_remaining'))
            total_base = total_remaining + total_pagu

            # --- Rumus ---
            persentasi_tl = (total_qty_kontrak / total_qty_izin_prinsip * 100) if total_qty_izin_prinsip > 0 else 0
            persentasi_droping = (total_droping / total_base * 100) if total_base > 0 else 0

            return {
                'persentasi_tl': "{:.2f}".format(persentasi_tl),
                'persentasi_droping': "{:.2f}".format(persentasi_droping),
            }




        

        if field == 'master_budget_list':
            masters = self.env['vit.master_budget'].search([], order="sequence, name")
            return {
                'master_list': [{'id': mb.id, 'name': mb.name} for mb in masters]
            }




        if field == 'master_budget_summary':
            izin_prinsip_list = self.env['vit.izin_prinsip'].search(domain_ip)
            master_ids = izin_prinsip_list.mapped('master_budget_id').ids
            kanwil_id = izin_prinsip_list[:1].kanwil_id.id if izin_prinsip_list else False

            master_budgets = self.env['vit.master_budget'].search([])
            budgets_domain = [('master_budget_id', 'in', master_ids)] + budget_date_domain
            budgets = self.env['vit.budget_rkap'].search(budgets_domain)

            master_summaries = []
            for mb in master_budgets:
                mb_budgets = budgets.filtered(lambda b: b.master_budget_id == mb)
                
                kontrak_ids = self.env['vit.kontrak'].search([
                    ('budget_rkap_id', 'in', mb_budgets.ids),
                    ('kanwil_id', '=', kanwil_id)
                ])

                izin_prinsip_filtered = self.env['vit.izin_prinsip'].search([
                    ('master_budget_id', '=', mb.id),
                    ('kanwil_id', '=', kanwil_id)
                ])


                if budget_date_domain:
                    tahun_rkap = False
                    if budgets:
                        tahun_rkap = budgets[0].budget_date.year 

                    allowed_master_ids = budgets.mapped('master_budget_id').ids if budgets else []
                    if allowed_master_ids:
                        izin_filtered_for_year = izin_prinsip_filtered.filtered(
                            lambda ip: ip.master_budget_id 
                            and ip.master_budget_id.id in allowed_master_ids
                            and any(b.master_budget_id.id == ip.master_budget_id.id and 
                                    b.budget_date.year == tahun_rkap for b in budgets)
                        )
                        total_pagu = sum(izin_filtered_for_year.mapped('total_pagu'))
                    else:
                        total_pagu = 0
                else:
                    total_pagu = sum(izin_prinsip_filtered.mapped('total_pagu'))



                if budget_date_domain:
                    tahun_rkap = False
                    if budgets:
                        tahun_rkap = budgets[0].budget_date.year

                    allowed_master_ids = budgets.mapped('master_budget_id').ids if budgets else []

                    if allowed_master_ids and mb.id in allowed_master_ids:
                        droping_all = self.env['vit.droping'].search([
                            ('master_budget_id', '=', mb.id),
                            ('kanwil_id', '=', kanwil_id)
                        ])

                        droping_filtered = droping_all.filtered(
                            lambda d: d.budget_date and d.budget_date.year == tahun_rkap
                        )
                    else:
                        droping_filtered = self.env['vit.droping'].browse()
                else:
                    droping_filtered = self.env['vit.droping'].search([
                        ('master_budget_id', '=', mb.id),
                        ('kanwil_id', '=', kanwil_id)
                    ])


                    
                if mb_budgets:
                    total_qty_izin_prinsip = sum(mb_budgets.mapped("total_qty_izin_prinsip")) / len(mb_budgets)
                    total_qty_kontrak = sum(mb_budgets.mapped("total_qty_kontrak")) / len(mb_budgets)
                else:
                    total_qty_izin_prinsip = 0
                    total_qty_kontrak = 0

                total_kontrak = sum(kontrak_ids.mapped('amount_kontrak'))
                total_droping = sum(droping_filtered.mapped('jumlah'))


                persen_kontrak = (total_qty_kontrak / total_qty_izin_prinsip * 100) if total_qty_izin_prinsip > 0 else 0
                total_base = (sum(mb_budgets.mapped("previous_remaining")) if mb_budgets else 0) + total_pagu
                persen_droping = (total_droping / total_base * 100) if total_base > 0 else 0


                master_summaries.append({
                    "master_budget": mb.name,
                    "remaining": sum(mb_budgets.mapped("previous_remaining")) if mb_budgets else 0,
                    "remaining_formatted": "{:,.0f}".format(sum(mb_budgets.mapped("previous_remaining")) if mb_budgets else 0).replace(",", "."),
                    "total_qty_izin_prinsip": sum(mb_budgets.mapped("total_qty_izin_prinsip")) if mb_budgets else 0,
                    # "total_qty_izin_prinsip": len(izin_prinsip_ids),
                    "total_pagu_izin_prinsip": total_pagu,
                    "total_pagu_izin_prinsip_formatted": "{:,.0f}".format(total_pagu).replace(",", "."),
                    "total_qty_kontrak": sum(mb_budgets.mapped("total_qty_kontrak")) if mb_budgets else 0,
                    # "total_qty_kontrak": len(kontrak_ids),
                    "total_amount_kontrak": total_kontrak,
                    "total_amount_kontrak_formatted": "{:,.0f}".format(total_kontrak).replace(",", "."),
                    "total_amount_droping": total_droping,
                    "total_amount_droping_formatted": "{:,.0f}".format(total_droping).replace(",", "."),
                    "persen_kontrak": round(persen_kontrak, 2),
                    "persen_droping": round(persen_droping, 2),
                })

            return {'master_summaries': master_summaries}


        # if field == 'master_budget_summary':
        #     izin_prinsip_list = self.env['vit.izin_prinsip'].search(domain_ip)
        #     master_ids = izin_prinsip_list.mapped('master_budget_id').ids
        #     kanwil_id = izin_prinsip_list[:1].kanwil_id.id if izin_prinsip_list else False

        #     master_budgets = self.env['vit.master_budget'].search([])
        #     budgets_domain = [('master_budget_id', 'in', master_ids)] + budget_date_domain
        #     budgets = self.env['vit.budget_rkap'].search(budgets_domain)

        #     master_summaries = []
        #     for mb in master_budgets:
        #         mb_budgets = budgets.filtered(lambda b: b.master_budget_id == mb)
                
        #         kontrak_ids = self.env['vit.kontrak'].search([
        #             ('budget_rkap_id', 'in', mb_budgets.ids),
        #             ('kanwil_id', '=', kanwil_id)
        #         ])

        #         izin_prinsip_filtered = self.env['vit.izin_prinsip'].search([
        #             ('master_budget_id', '=', mb.id),
        #             ('kanwil_id', '=', kanwil_id)
        #         ])

        #         # Hitung total_pagu_izin_prinsip
        #         if budget_date_domain:
        #             allowed_master_ids = budgets.mapped('master_budget_id').ids if budgets else []
        #             if allowed_master_ids:
        #                 izin_filtered_for_year = izin_prinsip_filtered.filtered(lambda ip: ip.master_budget_id and ip.master_budget_id.id in allowed_master_ids)
        #                 total_pagu = sum(izin_filtered_for_year.mapped('total_pagu'))
        #             else:
        #                 total_pagu = 0
        #         else:
        #             total_pagu = sum(izin_prinsip_filtered.mapped('total_pagu'))

        #         # Hitung total_qty_izin_prinsip
        #         if budget_date_domain:
        #             allowed_master_ids = budgets.mapped('master_budget_id').ids if budgets else []
        #             if allowed_master_ids:
        #                 izin_filtered_for_year = izin_prinsip_filtered.filtered(
        #                     lambda ip: ip.master_budget_id
        #                     and ip.master_budget_id.id in allowed_master_ids
        #                     and ip.kanwil_id.id == kanwil_id
        #                 )
        #                 total_qty_izin_prinsip = len(izin_filtered_for_year)
        #             else:
        #                 total_qty_izin_prinsip = 0
        #         else:
        #             izin_filtered = izin_prinsip_filtered.filtered(lambda ip: ip.kanwil_id.id == kanwil_id)
        #             total_qty_izin_prinsip = len(izin_filtered)


        #         # Hitung total_qty_kontrak berdasarkan master budget dan kanwil
        #         if budget_date_domain:
        #             allowed_master_ids = budgets.mapped('master_budget_id').ids if budgets else []
        #             if allowed_master_ids:
        #                 kontrak_filtered_for_year = kontrak_ids.filtered(
        #                     lambda k: k.budget_rkap_id.master_budget_id
        #                     and k.budget_rkap_id.master_budget_id.id in allowed_master_ids
        #                     and k.kanwil_id.id == kanwil_id
        #                 )
        #                 total_qty_kontrak = len(kontrak_filtered_for_year)
        #             else:
        #                 total_qty_kontrak = 0
        #         else:
        #             kontrak_filtered = kontrak_ids.filtered(lambda k: k.kanwil_id.id == kanwil_id)
        #             total_qty_kontrak = len(kontrak_filtered)



        #         # Hitung total_droping
        #         if budget_date_domain:
        #             allowed_master_ids = budgets.mapped('master_budget_id').ids if budgets else []
        #             if mb.id in allowed_master_ids:
        #                 droping_filtered = self.env['vit.droping'].search([
        #                     ('master_budget_id', '=', mb.id),
        #                     ('kanwil_id', '=', kanwil_id)
        #                 ])
        #             else:
        #                 droping_filtered = self.env['vit.droping'].browse()
        #         else:
        #             droping_filtered = self.env['vit.droping'].search([
        #                 ('master_budget_id', '=', mb.id),
        #                 ('kanwil_id', '=', kanwil_id)
        #             ])
        #         total_kontrak = sum(kontrak_ids.mapped('amount_kontrak'))
        #         total_droping = sum(droping_filtered.mapped('jumlah'))


        #         persen_kontrak = (total_kontrak / total_pagu * 100) if total_pagu > 0 else 0
        #         persen_droping = (total_droping / total_pagu * 100) if total_pagu > 0 else 0

        #         master_summaries.append({
        #             "master_budget": mb.name,
        #             "remaining": sum(mb_budgets.mapped("previous_remaining")) if mb_budgets else 0,
        #             "remaining_formatted": "{:,.0f}".format(sum(mb_budgets.mapped("previous_remaining")) if mb_budgets else 0).replace(",", "."),
        #             "total_qty_izin_prinsip": total_qty_izin_prinsip,
        #             "total_pagu_izin_prinsip": total_pagu,
        #             "total_pagu_izin_prinsip_formatted": "{:,.0f}".format(total_pagu).replace(",", "."),
        #             "total_qty_kontrak": total_qty_kontrak,
        #             "total_amount_kontrak": total_kontrak,
        #             "total_amount_kontrak_formatted": "{:,.0f}".format(total_kontrak).replace(",", "."),
        #             "total_amount_droping": total_droping,
        #             "total_amount_droping_formatted": "{:,.0f}".format(total_droping).replace(",", "."),
        #             "persen_kontrak": round(persen_kontrak, 2),
        #             "persen_droping": round(persen_droping, 2),
        #         })

        #     return {'master_summaries': master_summaries}





        
        # elif field == 'mahasiswa_inbound':
        #     domain = [('is_mahasiswa_inbound', '=', True)] + process_domain(domain, self.env['res.partner'])
        #     mahasiswa_inbound = self.env['res.partner'].search_count(domain)
        #     return {
        #         'total': mahasiswa_inbound,
        #     }

        # elif field == 'mahasiswa_outbound':
        #     domain =[('is_mahasiswa_outbound', '=', True)] + process_domain(domain, self.env['res.partner'])
        #     mahasiswa_outbound = self.env['res.partner'].search_count(domain)
        #     return {
        #         'total': mahasiswa_outbound,
        #     }

        # elif field == 'total_kunjungan_eksekutif':
        #     domain = process_domain(domain, self)
        #     kunjungan_eksekutif = self.env['vit.kunjungan_eksekutif'].search_count(domain)
        #     return {
        #         'total': kunjungan_eksekutif,
        #     }

        # elif field == 'total_kunjungan_mitra':
        #     domain = process_domain(domain, self)
        #     kunjungan_mitra = self.env['vit.kunjungan_mitra'].search_count(domain)
        #     return {
        #         'total': kunjungan_mitra,
        #     }

        elif field == 'total_kerjasama':
            domain = process_domain(domain, self)
            domain_aktif = [('status_id.name','=','Aktif')] + process_domain(domain, self)
            domain_tidak_aktif = [('status_id.name','=','Tidak Aktif')] + process_domain(domain, self)
            total_kerjasama = self.search_count(domain)
            total_kerjasama_aktif = self.search_count(domain_aktif)
            total_kerjasama_tidak_aktif = self.search_count(domain_tidak_aktif)
            return {
                'total': total_kerjasama,
                'total_aktif': total_kerjasama_aktif,
                'total_tidak_aktif': total_kerjasama_tidak_aktif,
            }

        elif field == 'total_kerjasama_mou':
            # print('total_kerjasama_mou',domain, field)
            
            domain = process_domain(domain, self)
            domain_aktif = [('status_id.name','=','Aktif')] + process_domain(domain, self)
            domain_tidak_aktif = [('status_id.name','=','Tidak Aktif')] + process_domain(domain, self)
            total_kerjasama_mou = self.search_count(domain)
            total_kerjasama_mou_aktif = self.search_count(domain_aktif)
            total_kerjasama_mou_tidak_aktif = self.search_count(domain_tidak_aktif)
            return {
                'total': total_kerjasama_mou,
                'total_aktif': total_kerjasama_mou_aktif,
                'total_tidak_aktif': total_kerjasama_mou_tidak_aktif,
            }

        elif field == 'total_kerjasama_moa':
            # moa = self.env['vit.jenis_dokumen'].search([('code', '=', 'MoA')])
            # domain =[('jenis_dokumen_id', '=', moa.id)] +   process_domain(domain, self.env['res.partner'])
            domain = process_domain(domain, self)
            domain_aktif = [('status_id.name','=','Aktif')] + process_domain(domain, self)
            domain_tidak_aktif = [('status_id.name','=','Tidak Aktif')] + process_domain(domain, self)
            total_kerjasama_moa = self.search_count(domain)
            total_kerjasama_moa_aktif = self.search_count(domain_aktif)
            total_kerjasama_moa_tidak_aktif = self.search_count(domain_tidak_aktif)
            return {
                'total': total_kerjasama_moa,
                'total_aktif': total_kerjasama_moa_aktif,
                'total_tidak_aktif': total_kerjasama_moa_tidak_aktif,
            }

        elif field == 'total_kerjasama_ia':
            # ia = self.env['vit.jenis_dokumen'].search([('code', '=', 'IA')])
            # domain =[('jenis_dokumen_id', '=', ia.id)] +   process_domain(domain, self.env['res.partner'])
            domain = process_domain(domain, self)
            domain_aktif = [('status_id.name','=','Aktif')] + process_domain(domain, self)
            domain_tidak_aktif = [('status_id.name','=','Tidak Aktif')] + process_domain(domain, self)
            total_kerjasama_ia = self.search_count(domain)
            total_kerjasama_ia_aktif = self.search_count(domain_aktif)
            total_kerjasama_ia_tidak_aktif = self.search_count(domain_tidak_aktif)
            return {
                'total': total_kerjasama_ia,
                'total_aktif': total_kerjasama_ia_aktif,
                'total_tidak_aktif': total_kerjasama_ia_tidak_aktif,
            }

        # elif field == 'total_kerjasama_by_status':
        #     domain = process_domain(domain, self)            
        #     where_clause, params = domain_to_sql(domain, self.env['vit.kerjasama_mitra_rel'])
        #     sql = f"""
        #         SELECT status.name as status_name, COUNT(*) as count
        #         FROM vit_kerjasama vk
        #         RIGHT JOIN vit_status_kegiatan as status ON vk.status_id = status.id
        #         LEFT JOIN vit_kerjasama_mitra_rel vkmr ON vk.id = vkmr.kerjasama_id                 
        #         WHERE 1=1 {where_clause}
        #         GROUP BY status.name
        #     """
        #     cr.execute(sql, params)
        #     res = cr.dictfetchall()
        #     total_kerjasama_by_status = {item['status_name']: item['count'] for item in res}
        #     # print('total_kerjasama_by_status',total_kerjasama_by_status)
        #     return {'total_kerjasama_by_status': total_kerjasama_by_status}

        # elif field == 'total_kerjasama_by_jenis':
        #     domain = process_domain(domain, self)
        #     where_clause, params = domain_to_sql(domain, self.env['vit.kerjasama_mitra_rel'])
        #     sql = f"""
        #         SELECT vk.jenis_kerjasama, COUNT(*) as count
        #         FROM vit_kerjasama vk
        #         LEFT JOIN vit_kerjasama_mitra_rel vkmr ON vk.id = vkmr.kerjasama_id                 
        #         WHERE 1=1 {where_clause}
        #         GROUP BY vk.jenis_kerjasama
        #     """
        #     # print('sql', sql)
        #     cr.execute(sql, params)
        #     res = cr.dictfetchall()
        #     total_kerjasama_by_jenis = {item['jenis_kerjasama']: item['count'] for item in res}
        #     # print('total_kerjasama_by_jenis',total_kerjasama_by_jenis)
        #     return {'total_kerjasama_by_jenis': total_kerjasama_by_jenis}

        # elif field == 'total_kerjasama_by_unit_kerja':
        #     domain = process_domain(domain, self)
        #     where_clause, params = domain_to_sql(domain, self.env['vit.kerjasama_mitra_rel'])
        #     sql = f"""
        #         SELECT
        #             ou.code AS operating_unit_name,
        #             COUNT(CASE WHEN sk.name = 'Aktif' THEN 1 END) AS total_aktif,
        #             COUNT(CASE WHEN sk.name = 'Tidak Aktif' THEN 1 END) AS total_tidak_aktif
        #         FROM
        #             operating_unit ou
        #         LEFT JOIN
        #             vit_kerjasama vk ON vk.operating_unit_id = ou.id
        #         LEFT JOIN
        #             vit_status_kegiatan sk ON vk.status_id = sk.id
        #         LEFT JOIN
        #             vit_kerjasama_mitra_rel vkmr ON vkmr.kerjasama_id = vk.id
        #         WHERE 1=1 {where_clause}
        #         GROUP BY
        #             ou.code
        #         UNION ALL
        #         SELECT
        #             'Tanpa Unit' AS operating_unit_name,
        #             COUNT(CASE WHEN sk.name = 'Aktif' THEN 1 END) AS total_aktif,
        #             COUNT(CASE WHEN sk.name = 'Tidak Aktif' THEN 1 END) AS total_tidak_aktif
        #         FROM
        #             vit_kerjasama vk
        #         LEFT JOIN
        #             vit_status_kegiatan sk ON vk.status_id = sk.id
        #         LEFT JOIN
        #             vit_kerjasama_mitra_rel vkmr ON vkmr.kerjasama_id = vk.id
        #         WHERE vk.operating_unit_id IS NULL {where_clause}
        #         GROUP BY
        #             operating_unit_name
        #         ORDER BY
        #             operating_unit_name;
        #     """
        #     # print('sql', sql)
        #     cr.execute(sql, params*2)
        #     res = cr.dictfetchall()
        #     total_kerjasama_by_unit_kerja = {}
        #     for item in res:
        #         operating_unit_name = item['operating_unit_name']
        #         total_aktif = item['total_aktif']
        #         total_tidak_aktif = item['total_tidak_aktif']
        #         total_kerjasama_by_unit_kerja[operating_unit_name] = {
        #             'Aktif': total_aktif,
        #             'Tidak Aktif': total_tidak_aktif
        #         }
        #     # print('total_kerjasama_by_unit_kerja',total_kerjasama_by_unit_kerja)
        #     return {'total_kerjasama_by_unit_kerja': total_kerjasama_by_unit_kerja}

        # elif field == 'total_kerjasama_by_year_and_type':
        #     domain = process_domain(domain, self)
        #     where_clause, params = domain_to_sql(domain, self.env['vit.kerjasama_mitra_rel'])
        #     sql = f"""
        #         SELECT extract('year' from vk.tanggal_awal) as year, vk.jenis_kerjasama, COUNT(*) as count
        #         FROM vit_kerjasama vk
        #         LEFT JOIN vit_kerjasama_mitra_rel vkmr ON vk.id = vkmr.kerjasama_id 
        #         WHERE vk.tanggal_awal IS NOT NULL {where_clause}
        #         GROUP BY extract('year' from vk.tanggal_awal), vk.jenis_kerjasama
        #         ORDER BY year
        #     """
        #     cr.execute(sql, params)
        #     res = cr.dictfetchall()
        #     total_kerjasama_by_year_and_type = {}
        #     for item in res:
        #         year = int(item['year'])
        #         jenis_kerjasama = item['jenis_kerjasama']
        #         count = item['count']
        #         if year not in total_kerjasama_by_year_and_type:
        #             total_kerjasama_by_year_and_type[year] = {"DN": 0, "LN": 0}
        #         total_kerjasama_by_year_and_type[year][jenis_kerjasama] = count

        #     # print('total_kerjasama_by_year_and_type',total_kerjasama_by_year_and_type)
        #     return {'total_kerjasama_by_year_and_type': total_kerjasama_by_year_and_type}

        elif field == 'list':
            domain = process_domain(domain, self)
            total_count = self.search_count(domain)
            res = self.search_read(domain, fields=['id','name', 'judul','keterangan', 'nama_mitra', 
                                                   'mitra_location', 'tanggal_awal', 
                                                   'jenis_dokumen_id', 'operating_unit_id', 
                                                   'status_id',
                                                   'bidang_kerjasama_id'], order='tanggal_berakhir desc', limit=limit, offset=offset)
            return {'data': res, 'total': total_count}
        
        else:
            return {'error': 'unknown field'}

    # @api.model
    # def get_locations(self, domain=None):
    #     cr = self.env.cr
    #     domain = process_domain(domain, self)
    #     where_clause, params = domain_to_sql(domain, self.env['vit.kerjasama_mitra_rel'])
    #     sql = f"""
    #         SELECT p.id, p.name, 
    #             coalesce(p.partner_latitude,0) as partner_latitude, 
    #             coalesce(p.partner_longitude,0) as partner_longitude,
    #             p.initial,
    #             p.country_id, p.region_id,
    #             c.name->>'en_US' as country_name, 
    #             r.name as region_id
    #         FROM vit_kerjasama_mitra_rel vkmr
    #         LEFT JOIN res_partner p on vkmr.name = p.id
    #         LEFT JOIN res_country c on p.country_id = c.id
    #         LEFT JOIN vit_region r on c.region_id = r.id
    #         WHERE 1=1
    #         AND p.partner_latitude != 0
    #         AND p.partner_longitude != 0
    #         and p.is_mitra = true
    #         {where_clause}
    #     """
    #     cr.execute(sql, params)
    #     partner_locations = cr.dictfetchall()
    #     return partner_locations



    @api.model
    def get_statistics_sarlog(self):
        master_budgets = self.env["vit.master_budget"].search([])
        result = []

        total_all_pagu = 0
        total_all_realisasi = 0

        for mb in master_budgets:
            budgets = self.search([("master_budget_id", "=", mb.id)])

            pagu = sum(budgets.mapped("total_pagu_izin_prinsip")) if "total_pagu_izin_prinsip" in budgets._fields else 0
            realisasi = sum(budgets.mapped("total_amount_payment")) if "total_amount_payment" in budgets._fields else 0

            persen_realisasi = (realisasi / pagu * 100) if pagu > 0 else 0

            result.append({
                "id": mb.id,
                "name": mb.name,
                "pagu_izin_prinsip": pagu,
                "realisasi": realisasi,
                "persen_realisasi": round(persen_realisasi, 2),
            })

            total_all_pagu += pagu
            total_all_realisasi += realisasi

        total_persen = (total_all_realisasi / total_all_pagu * 100) if total_all_pagu > 0 else 0

        return {
            "master_list": result,
            "total_summary": {
                "pagu": total_all_pagu,
                "realisasi": total_all_realisasi,
                "persen": round(total_persen, 2),
            },
        }
    
    # @api.model
    # def get_droping_by_kanwil(self):
    #     """
    #     Ambil data persentase droping per kanwil
    #     untuk ditampilkan di bar chart dashboard Sarlog.
    #     """
    #     kanwils = self.env["vit.kanwil"].search([])
    #     result = []

    #     for kw in kanwils:
    #         izin_prinsip_list = self.env['vit.izin_prinsip'].search([('kanwil_id', '=', kw.id)])
    #         master_ids = izin_prinsip_list.mapped('master_budget_id').ids
    #         budgets = self.search([('master_budget_id', 'in', master_ids)])

    #         total_pagu = sum(budgets.mapped('total_pagu_izin_prinsip')) or 0
    #         total_droping = sum(budgets.mapped('total_amount_droping')) or 0
    #         persen_droping = (total_droping / total_pagu * 100) if total_pagu > 0 else 0

    #         result.append({
    #             "kanwil_name": kw.name,
    #             "persen_droping": round(persen_droping, 2),
    #         })

    #     return result



    @api.model
    def get_droping_by_kanwil(self):
        """
        Ambil data persentase droping per kanwil
        PAKAI logika yang sama seperti field 'persentase_tl_droping'
        """
        kanwils = self.env["vit.kanwil"].search([])
        result = []

        for kw in kanwils:
            izin_prinsip_list = self.env['vit.izin_prinsip'].search([('kanwil_id', '=', kw.id)])
            master_ids = izin_prinsip_list.mapped('master_budget_id').ids

            budgets = self.env['vit.budget_rkap'].search([
                ('master_budget_id', 'in', master_ids)
            ])

            amount = sum(budgets.mapped('amount')) or 0
            total_realisasi = sum(budgets.mapped('total_amount_payment')) or 0

            droping_domain = [('master_budget_id', 'in', master_ids), ('kanwil_id', '=', kw.id)]
            droping_filtered = self.env['vit.droping'].search(droping_domain)
            total_droping = sum(droping_filtered.mapped('jumlah')) or 0

            persentasi_droping = (total_realisasi / total_droping * 100) if total_droping > 0 else 0

            result.append({
                "kanwil_name": kw.name,
                "persen_droping": round(persentasi_droping, 2),
            })

        return result
    


    @api.model
    def get_realisasi_by_kanwil(self):
        """
        Ambil data persentase realisasi (TL) per kanwil
        PAKAI logika yang sama seperti field 'persentase_tl_droping'
        yaitu: persentase_tl = total_realisasi / total_amount_budget * 100
        """
        kanwils = self.env["vit.kanwil"].search([])
        result = []

        for kw in kanwils:
            izin_prinsip_list = self.env['vit.izin_prinsip'].search([('kanwil_id', '=', kw.id)])
            record = izin_prinsip_list[:1]
            master_ids = izin_prinsip_list.mapped('master_budget_id').ids
            kanwil_id = record.kanwil_id.id if record else False

            budgets = self.env['vit.budget_rkap'].search([
                ('master_budget_id', 'in', master_ids)
            ])
            amount = sum(budgets.mapped('amount'))
            total_realisasi = sum(budgets.mapped('total_amount_payment'))

            droping_domain = [('master_budget_id', 'in', master_ids)]
            if kanwil_id:
                droping_domain.append(('kanwil_id', '=', kanwil_id))
            droping_filtered = self.env['vit.droping'].search(droping_domain)
            total_droping = sum(droping_filtered.mapped('jumlah'))

            persentase_tl = (total_realisasi / amount * 100) if amount > 0 else 0

            result.append({
                "kanwil_name": kw.name,
                "persen_realisasi": round(persentase_tl, 2),
            })

        return result










            