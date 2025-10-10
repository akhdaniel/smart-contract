from odoo import models, fields, api, _
from odoo.exceptions import UserError

class master_budget(models.Model):

    _name = "vit.master_budget"
    _inherit = "vit.master_budget"


    sequence = fields.Integer(string="Sequence", default=10)