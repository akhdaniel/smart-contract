
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class izin_prinsip(models.Model):
    _name = "vit.izin_prinsip_line"
    _inherit = "vit.izin_prinsip_line"

    name = fields.Char( required=False, copy=False, string=_("Name"))

    jenis_kontrak_id = fields.Many2one(
        comodel_name="vit.jenis_kontrak",
        required=True,
        string=_("Jenis Kontrak"),
    )


    kanwil_id = fields.Many2one(
        comodel_name="vit.kanwil",
        string="Kanwil",
        related="job_izin_prinsip_id.izin_prinsip_id.kanwil_id",
    )


    kanca_id = fields.Many2one(
        comodel_name="vit.kanca",
        string="Kanca",
        related="job_izin_prinsip_id.kanca_id",
    )