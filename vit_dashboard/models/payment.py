# -*- coding: utf-8 -*-

from odoo import models, api
import logging
_logger = logging.getLogger(__name__)
from .tools import domain_to_sql, process_domain

class Lead(models.Model):
    _inherit = 'crm.lead'


    @api.model
    def get_statistics(self, domain=None, field=None):
        # print('domain', domain)
        domain = domain or []  # Use an empty domain if none is provided
        cr = self.env.cr

        if field == 'total_lead_by_stage':
            domain = process_domain(domain, self)                    
            where_clause, params = domain_to_sql(domain, self.env['crm.lead'])
            sql = f"""
                SELECT s.sequence,s.name->>'en_US' as stage_name, COUNT(*) as count
                FROM crm_lead l
                LEFT JOIN crm_stage s ON s.id = l.stage_id
                WHERE s.name->>'en_US' <> 'Penandatangan' and 1=1 {where_clause}
                GROUP BY s.sequence,s.name
                ORDER BY s.sequence
            """
            cr.execute(sql, params)
            res = cr.dictfetchall()
            total_lead_by_stage = {}
            for item in res:
                stage_name = item['stage_name']
                total_lead_by_stage[stage_name] = {"Jumlah": item["count"]}

            return {'total_lead_by_stage': total_lead_by_stage}
        
        elif field == 'total_lead_by_unit_kerja':
            domain = process_domain(domain, self)                    
            where_clause, params = domain_to_sql(domain, self.env['crm.lead'])
            sql = f"""
                SELECT ou.code as unit_name,
                    COUNT(l.id) as count
                FROM operating_unit ou
                LEFT JOIN crm_lead l ON ou.id = l.operating_unit_id
                WHERE 1=1 {where_clause}
                GROUP BY ou.code
                UNION ALL
                SELECT 'TANPA UNIT' as unit_name,
                    COUNT(l.id) as count
                FROM crm_lead l
                WHERE l.operating_unit_id IS NULL {where_clause}
                GROUP BY unit_name
                ORDER BY unit_name
            """
            cr.execute(sql, params*2)
            res = cr.dictfetchall()
            # total_lead_by_unit_kerja = {item['unit_name']: item['count'] for item in res}
            
            total_lead_by_unit_kerja = {}
            for item in res:
                unit_name = item['unit_name'] or 'TANPA UNIT'
                total_lead_by_unit_kerja[unit_name] = {"Jumlah": item["count"]}

            return {'total_lead_by_unit_kerja': total_lead_by_unit_kerja}
        
        else:
            return {'error': 'unknown field'}


