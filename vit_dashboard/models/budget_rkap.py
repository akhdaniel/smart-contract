# -*- coding: utf-8 -*-

from odoo import models, api
import logging
_logger = logging.getLogger(__name__)
from .tools import domain_to_sql, process_domain

class budget_rkap(models.Model):
    _inherit = 'vit.budget_rkap'

    @api.model
    def get_statistics(self, domain=None, field=None, limit=10, offset=0):
        """
        This method is used to get the statistics of the partners.
        :param domain: Optional domain to filter the records.
        :param field: The specific field or statistic to retrieve.
        :return: Dictionary containing the requested statistics.
        """
        
        domain = domain or []  # Use an empty domain if none is provided
        cr = self.env.cr

        # if field == 'total_budget_realisasi':
        #     # domain = [('kanwil_kancab_id', '=',[])] + (domain, self)
        #     domain = []
        #     amount = sum(self.env['vit.budget_rkap'].search(domain).mapped('amount'))
        #     total_realisasi = sum(self.env['vit.budget_rkap'].search(domain).mapped('total_amount_payment'))
        #     persentasi = (total_realisasi / amount * 100) if amount > 0 else 0
        #     return {
        #         'amount': amount,
        #         'total_realisasi': total_realisasi,
        #         'persentasi': persentasi,
        #     }
        
        if field == 'total_budget_realisasi':
            # contoh ambil satu record
            record = self.env['vit.budget_rkap'].search([], limit=1)

            domain = []
            if record.kanwil_kancab_id:
                domain = [('kanwil_kancab_id', '=', record.kanwil_kancab_id.id)]

            budgets = self.env['vit.budget_rkap'].search(domain)
            amount = sum(budgets.mapped('amount'))
            total_realisasi = sum(budgets.mapped('total_amount_payment'))
            persentasi = (total_realisasi / amount * 100) if amount > 0 else 0

            return {
                'kanwil_name': record.kanwil_kancab_id.name if record.kanwil_kancab_id else '',
                'amount': amount,
                'total_realisasi': total_realisasi,
                'persentasi': persentasi,
            }
        
        if field == 'master_budget_summary':
            record = self.env['vit.budget_rkap'].search([], limit=1)
            domain = []
            if record.kanwil_kancab_id:
                domain = [('kanwil_kancab_id', '=', record.kanwil_kancab_id.id)]

            budgets = self.env['vit.budget_rkap'].search(domain)
            master_summaries = []
            for mb in budgets.mapped("master_budget_id"):
                mb_budgets = budgets.filtered(lambda b: b.master_budget_id == mb)

                total_pagu = sum(mb_budgets.mapped("total_pagu_izin_prinsip")) or 0
                total_kontrak = sum(mb_budgets.mapped("total_amount_kontrak")) or 0
                total_droping = sum(mb_budgets.mapped("total_amount_droping")) or 0

                persen_kontrak = (total_kontrak / total_pagu * 100) if total_pagu > 0 else 0
                persen_droping = (total_droping / total_pagu * 100) if total_pagu > 0 else 0

                master_summaries.append({
                    "master_budget": mb.name,
                    "remaining": sum(mb_budgets.mapped("remaining")),
                    "total_qty_izin_prinsip": sum(mb_budgets.mapped("total_qty_izin_prinsip")),
                    "total_pagu_izin_prinsip": total_pagu,
                    "total_qty_kontrak": sum(mb_budgets.mapped("total_qty_kontrak")),
                    "total_amount_kontrak": total_kontrak,
                    "total_amount_droping": total_droping,
                    "persen_kontrak": persen_kontrak,
                    "persen_droping": persen_droping,
                })

            return {
                'master_summaries': master_summaries,
            }





        
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
        