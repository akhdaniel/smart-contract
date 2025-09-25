# -*- coding: utf-8 -*-

from odoo import models, api
import logging
_logger = logging.getLogger(__name__)
from .tools import domain_to_sql, process_domain

class KunjunganMitra(models.Model):
    _inherit = 'vit.kunjungan_mitra'


    @api.model
    def get_statistics(self, domain=None, field=None):
        if field == 'total_kunjungan_mitra':
            domain = process_domain(domain, self)
            kunjungan_mitra = self.env['vit.kunjungan_mitra'].search_count(domain)
            return {
                'total': kunjungan_mitra,
            }
    
        else:
            return {'error': 'unknown field'}


