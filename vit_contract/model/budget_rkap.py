#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class budget_rkap(models.Model):

    _name = "vit.budget_rkap"
    _description = "vit.budget_rkap"


    def download_budget(self, ):
        pass


    def action_reload_view(self):
        pass

    name = fields.Char( required=True, copy=False, default="New", readonly=True,  string=_("Name"))
    amount = fields.Float( string=_("Amount"))
    remaining = fields.Float( string=_("Remaining"))
    total_pagu_izin_prinsip = fields.Float( string=_("Total Pagu Izin Prinsip"))
    total_amount_kontrak = fields.Float( string=_("Total Amount Kontrak"))
    total_amount_payment = fields.Float( string=_("Total Amount Payment"))
    total_qty_izin_prinsip = fields.Integer( string=_("Total Qty Izin Prinsip"))
    total_qty_kontrak = fields.Integer( string=_("Total Qty Kontrak"))
    total_qty_termin = fields.Integer( string=_("Total Qty Termin"))
    total_amount_droping = fields.Float( string=_("Total Amount Droping"))
    budget_date = fields.Date( string=_("Budget Date"))
    previous_remaining = fields.Float( string=_("Previous Remaining"))
    stage_is_draft = fields.Boolean(related="stage_id.draft", store=True,  string=_("Stage Is Draft"))
    stage_is_done = fields.Boolean(related="stage_id.done", store=True,  string=_("Stage Is Done"))
    allow_confirm = fields.Boolean(related="stage_id.allow_confirm", store=True,  string=_("Allow Confirm"))
    allow_cancel = fields.Boolean(related="stage_id.allow_cancel", store=True,  string=_("Allow Cancel"))
    stage_name = fields.Char(related="stage_id.name", store=True,  string=_("Stage Name"))
    jenis_penugasan = fields.Selection(selection=[('pso', 'Pso'),('kom', 'Kom')],  string=_("Jenis Penugasan"))
    tipe_kegiatan = fields.Selection(selection=[('biaya', 'Biaya'),('investasi', 'Investasi')],  string=_("Tipe Kegiatan"))


    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if not val.get("name", False) or val["name"] == "New":
                val["name"] = self.env["ir.sequence"].next_by_code("vit.budget_rkap") or "Error Number!!!"
        return super(budget_rkap, self).create(vals)

    def _get_first_stage(self):
        try:
            data_id = self.env["vit.state_budget"].sudo().search([], limit=1, order="sequence asc")
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
        data_id = self.env["vit.state_budget"].sudo().search([("sequence",">",current_stage_seq)], limit=1, order="sequence asc")
        if data_id:
            return data_id
        else:
            return self.stage_id

    def _get_previous_stage(self):
        current_stage_seq = self.stage_id.sequence
        data_id = self.env["vit.state_budget"].sudo().search([("sequence","<",current_stage_seq)], limit=1, order="sequence desc")
        if data_id:
            return data_id
        else:
            return self.stage_id

    @api.model
    def _group_expand_states(self, stages, domain, order):
        return self.env['vit.state_budget'].search([])

    def unlink(self):
        for me_id in self :
            if not me_id.stage_id.draft:
                raise UserError("Cannot delete non draft record!  Make sure that the Stage draft flag is checked.")
        return super(budget_rkap, self).unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)'
        })
        return super(budget_rkap, self).copy(default)

    izin_prinsip_ids = fields.One2many(comodel_name="vit.izin_prinsip",  inverse_name="budget_id",  string=_("Izin Prinsip"))
    master_budget_id = fields.Many2one(comodel_name="vit.master_budget",  string=_("Master Budget"))
    stage_id = fields.Many2one(comodel_name="vit.state_budget",  default=_get_first_stage, copy=False, group_expand="_group_expand_states",  string=_("Stage"))
    kontrak_ids = fields.One2many(comodel_name="vit.kontrak",  inverse_name="budget_rkap_id",  string=_("Kontrak"))
    payment_ids = fields.One2many(comodel_name="vit.payment",  inverse_name="budget_rkap_id",  string=_("Payment"))
