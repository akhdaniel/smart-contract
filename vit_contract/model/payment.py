#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class payment(models.Model):

    _name = "vit.payment"
    _description = "vit.payment"


    def kirim_request_pembayaran(self, ):
        pass


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, default="New", readonly=True,  string=_("Name"))
    amount = fields.Float(readonly=True,  string=_("Amount"))
    stage_is_draft = fields.Boolean(related="stage_id.draft", store=True,  string=_("Stage Is Draft"))
    stage_is_done = fields.Boolean(related="stage_id.done", store=True,  string=_("Stage Is Done"))
    allow_confirm = fields.Boolean(related="stage_id.allow_confirm", store=True,  string=_("Allow Confirm"))
    allow_cancel = fields.Boolean(related="stage_id.allow_cancel", store=True,  string=_("Allow Cancel"))
    stage_name = fields.Char(related="stage_id.name", store=True,  string=_("Stage Name"))
    request_date = fields.Date( string=_("Request Date"))
    payment_date = fields.Date( string=_("Payment Date"))
    amount_denda = fields.Float( string=_("Amount Denda"))
    amount_budget_rkap = fields.Float( string=_("Amount Budget Rkap"))
    amount_izin_prinsip = fields.Float( string=_("Amount Izin Prinsip"))
    amount_kontrak = fields.Float( string=_("Amount Kontrak"))
    syarat_progress = fields.Float( string=_("Syarat Progress"))
    actual_progress = fields.Float( string=_("Actual Progress"))
    syarat_output = fields.Text( string=_("Syarat Output"))
    actual_output = fields.Text( string=_("Actual Output"))
    persentase = fields.Float( string=_("Persentase"))
    stage_is_on_progress = fields.Boolean(related="stage_id.on_progress", store=True,  string=_("Stage Is On Progress"))


    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if not val.get("name", False) or val["name"] == "New":
                val["name"] = self.env["ir.sequence"].next_by_code("vit.payment") or "Error Number!!!"
        return super(payment, self).create(vals)

    def _get_first_stage(self):
        try:
            data_id = self.env["vit.state_payment"].sudo().search([], limit=1, order="sequence asc")
            if data_id:
                return data_id
        except KeyError:
            return False

    def action_confirm(self):
        stage = self._get_next_stage()
        self.stage_id=stage
        if self.stage_id.execute_enter and hasattr(self, self.stage_id.execute_enter) and callable(getattr(self, self.stage_id.execute_enter)):
            eval(f"self.{self.stage_id.execute_enter}()")

    def action_cancel(self):
        stage = self._get_previous_stage()
        self.stage_id=stage

    def _get_next_stage(self):
        current_stage_seq = self.stage_id.sequence
        data_id = self.env["vit.state_payment"].sudo().search([("sequence",">",current_stage_seq)], limit=1, order="sequence asc")
        if data_id:
            return data_id
        else:
            return self.stage_id

    def _get_previous_stage(self):
        current_stage_seq = self.stage_id.sequence
        data_id = self.env["vit.state_payment"].sudo().search([("sequence","<",current_stage_seq)], limit=1, order="sequence desc")
        if data_id:
            return data_id
        else:
            return self.stage_id

    @api.model
    def _group_expand_states(self, stages, domain, order):
        return self.env['vit.state_payment'].search([])

    def unlink(self):
        for me_id in self :
            if not me_id.stage_id.draft:
                raise UserError("Cannot delete non draft record!  Make sure that the Stage draft flag is checked.")
        return super(payment, self).unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(payment, self).copy(default)

    partner_id = fields.Many2one(comodel_name="res.partner",  string=_("Partner"))
    budget_rkap_id = fields.Many2one(comodel_name="vit.budget_rkap",  string=_("Budget Rkap"))
    termin_id = fields.Many2one(comodel_name="vit.termin",  string=_("Termin"))
    master_budget_id = fields.Many2one(comodel_name="vit.master_budget",  string=_("Master Budget"))
    kanwil_id = fields.Many2one(comodel_name="vit.kanwil",  string=_("Kanwil"))
    kontrak_id = fields.Many2one(comodel_name="vit.kontrak",  string=_("Kontrak"))
    stage_id = fields.Many2one(comodel_name="vit.state_payment",  default=_get_first_stage, copy=False, group_expand="_group_expand_states",  string=_("Stage"))
    master_nama_termin_id = fields.Many2one(comodel_name="vit.master_nama_termin",  string=_("Master Nama Termin"))
    izin_prinsip_id = fields.Many2one(comodel_name="vit.izin_prinsip",  string=_("Izin Prinsip"))
