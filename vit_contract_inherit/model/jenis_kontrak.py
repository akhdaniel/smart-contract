from odoo import models, fields, api, _
from odoo.exceptions import UserError

class jenis_kontrak(models.Model):

    _name = "vit.jenis_kontrak"
    _inherit = "vit.jenis_kontrak"


    type = fields.Selection(
        selection=[
            ('fisik', 'Fisik'),
            ('non_fisik', 'Non Fisik')
        ],  
        string=_("Type"),
        default='non_fisik',
    )