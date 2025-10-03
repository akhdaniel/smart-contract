from odoo import models, fields, api, _
from odoo.exceptions import UserError

class master_nama_termin(models.Model):

    _name = "vit.master_nama_termin"
    _inherit = "vit.master_nama_termin"
    _order = "sequence asc"

    type = fields.Selection(
        selection=[
            ('is_dp', 'DP'),
            ('is_retensi', 'Retensi'),
            ('is_termin', 'Termin')
        ],
        string=_("Type"),
        default='is_termin'
    )

    sequence = fields.Integer(
        string="Sequence",
        default=10
    )




    @api.model
    def create(self, vals):
        if vals.get("type") == "is_retensi":
            last_seq = self.search([], order="sequence desc", limit=1).sequence
            vals["sequence"] = (last_seq or 0) + 100
        else:
            retensi = self.search([("type", "=", "is_retensi")], limit=1)
            if retensi:
                last_non_retensi = self.search(
                    [("id", "!=", retensi.id), ("type", "!=", "is_retensi")],
                    order="sequence desc",
                    limit=1
                )
                if last_non_retensi:
                    vals["sequence"] = last_non_retensi.sequence + 10
                else:
                    vals["sequence"] = 10
            else:
                last_seq = self.search([], order="sequence desc", limit=1).sequence
                vals["sequence"] = (last_seq or 0) + 10

        return super().create(vals)


    