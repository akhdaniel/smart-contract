# -*- coding: utf-8 -*-

from odoo import models, api
import logging
_logger = logging.getLogger(__name__)
from .tools import domain_to_sql, process_domain

class KunjunganEksekutif(models.Model):
    _inherit = 'vit.kunjungan_eksekutif'


    @api.model
    def get_statistics(self, domain=None, field=None):
        if field == 'total_kunjungan_eksekutif':
            domain = process_domain(domain, self)
            kunjungan_eksekutif = self.env['vit.kunjungan_eksekutif'].search_count(domain)
            return {
                'total': kunjungan_eksekutif,
            }
    
        else:
            return {'error': 'unknown field'}


