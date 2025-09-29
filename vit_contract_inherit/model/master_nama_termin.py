from odoo import models, fields, api, _
from odoo.exceptions import UserError

class master_nama_termin(models.Model):

    _name = "vit.master_nama_termin"
    _inherit = "vit.master_nama_termin"

    type = fields.Selection(
        selection=[
            ('is_dp', 'DP'),
            ('is_retensi', 'Retensi'),
            ('is_termin', 'Termin')
        ],
        string=_("Type"),
        default='is_termin'
    )


    