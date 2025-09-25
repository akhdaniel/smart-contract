
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class izin_prinsip(models.Model):
    _name = "vit.izin_prinsip_line"
    _inherit = "vit.izin_prinsip_line"

    name = fields.Char( required=False, copy=False, string=_("Name"))
    kanwil_kancab_id = fields.Many2one(comodel_name="vit.kanwil_kancab", related="izin_prinsip_id.kanwil_kancab_id", string="Kanwil", store=True)


    @api.constrains('jenis_kontrak_id', 'izin_prinsip_id')
    def _check_duplicate_jenis_kontrak(self):
        for rec in self:
            if rec.jenis_kontrak_id and rec.izin_prinsip_id:
                dupe = rec.izin_prinsip_id.izin_prinsip_line_ids.filtered(
                    lambda l: l.id != rec.id and l.jenis_kontrak_id == rec.jenis_kontrak_id
                )
                if dupe:
                    raise ValidationError(
                        _("Jenis Kontrak %s sudah ada di Izin Prinsip %s, tidak boleh duplikat!") 
                        % (rec.jenis_kontrak_id.name, rec.izin_prinsip_id.name)
                    )