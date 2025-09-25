# -*- coding: utf-8 -*-

from odoo import models, api
import logging
_logger = logging.getLogger(__name__)
from .tools import domain_to_sql, process_domain

class ResPartner(models.Model):
    _inherit = 'res.partner'


    @api.model
    def get_statistics(self, domain=None, field=None):
        domain = domain or []  
        cr = self.env.cr

        if field == 'mahasiswa_inbound':
            domain = process_domain(domain, self.env['res.partner'])
            mahasiswa_inbound = self.env['res.partner'].search_count(domain)
            return {
                'total': mahasiswa_inbound,
            }
        
        elif field == 'mahasiswa_outbound':
            domain = process_domain(domain, self.env['res.partner'])
            mahasiswa_outbound = self.env['res.partner'].search_count(domain)
            return {
                'total': mahasiswa_outbound,
            }

        elif field == 'total_pertukaran_by_unit_kerja':
            domain = process_domain(domain, self)                    
            where_clause, params = domain_to_sql(domain, self.env['res.partner'])
            sql = f"""
                SELECT
                    ou.id AS operating_unit_id,
                    ou.code AS operating_unit_name,
                    COUNT(CASE WHEN rp.is_mahasiswa_inbound = TRUE THEN 1 END) AS total_inbound,
                    COUNT(CASE WHEN rp.is_mahasiswa_outbound = TRUE THEN 1 END) AS total_outbound
                FROM
                    operating_unit ou
                LEFT JOIN
                    res_partner rp ON rp.operating_unit_id = ou.id
                WHERE 1=1 {where_clause}
                GROUP BY
                    ou.id, ou.code
                ORDER BY
                    ou.code;
            """
            cr.execute(sql, params)
            res = cr.dictfetchall()
            total_pertukaran_by_unit_kerja = {}
            for item in res:
                operating_unit_name = item['operating_unit_name']
                total_inbound = item['total_inbound']
                total_outbound = item['total_outbound']
                total_pertukaran_by_unit_kerja[operating_unit_name] = {
                    'Inbound': total_inbound,
                    'Outbound': total_outbound,
                }

            return {'total_pertukaran_by_unit_kerja': total_pertukaran_by_unit_kerja}

        else:
            return {'error': 'unknown field'}