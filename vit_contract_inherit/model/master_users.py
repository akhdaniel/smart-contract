from odoo import models, fields, api, _
from odoo.exceptions import UserError

class master_users(models.Model):

    _inherit = "vit.master_users"


    def action_reload_view(self):
        pass

    name = fields.Char( required=False, copy=False, string=_("Nama Vendor"))