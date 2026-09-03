from odoo import models, fields, api
from datetime import datetime


class RealisasiSarlogDashboard(models.TransientModel):
    _name = 'wizard.realisasi.sarlog.dashboard'
    _description = 'Wizard Realisasi Sarlog Dashboard'

    year = fields.Selection(selection='_get_available_years', string='Tahun', required=True)

    @api.model
    def _get_available_years(self):
        current_year = datetime.now().year
        years = [(str(year), str(year)) for year in range(current_year - 5, current_year + 1)]
        return years

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res['year'] = str(datetime.now().year)
        return res

    def action_export_excel(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Realisasi Sarlog Dashboard',
                'message': 'Template Excel belum dibuat.',
                'type': 'warning',
                'sticky': False,
            }
        }
