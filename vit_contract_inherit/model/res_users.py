from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    multi_kanwil = fields.Many2many(
        'vit.kanwil',
        'res_users_multi_kanwil_rel',
        'user_id',
        'kanwil_id',
        string='Allowed Kanwil',
        help='Pilih beberapa Kanwil yang diizinkan untuk user ini.'
    )

    multi_kanca = fields.Many2many(
        'vit.kanca',
        'res_users_multi_kanca_rel',
        'user_id',
        'kanca_id',
        string='Allowed Kanca',
        domain="[('id', 'in', multi_kanca_domain_ids)]",
        help='Pilih beberapa Kanca yang diizinkan untuk user ini.'
    )


    multi_kanca_domain_ids = fields.Many2many(
        'vit.kanca',
        compute='_compute_multi_kanca_domain',
        string='Multi Kanca Domain',
    )

    @api.depends('multi_kanwil')
    def _compute_multi_kanca_domain(self):
        for rec in self:
            domain = []
            if rec.multi_kanwil:
                domain = [('kanwil_id', 'in', rec.multi_kanwil.ids)]
            else:
                domain = [('id', '=', 0)]

            rec.multi_kanca_domain_ids = self.env['vit.kanca'].search(domain)


    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)

        for user, vals in zip(users, vals_list):

            name = vals.get('name')
            if not name:
                continue

            lower_name = name.lower().strip()

            # =====================================================
            # 1. SPECIAL CASE: Kanwil Umum atau Kanwil Keuangan
            # =====================================================
            if "kanwil umum" in lower_name or "kanwil keuangan" in lower_name:
                kanwil = self.env['vit.kanwil'].search([
                    ('name', 'ilike', name)
                ], limit=1)

                if kanwil:
                    user.write({'multi_kanwil': [(4, kanwil.id)]})

                continue


            # =====================================================
            # 2. Selain itu → dianggap KANCA
            # =====================================================
            # if lower_name.startswith("kanwil") or lower_name.startswith("kanca"):

            #     cleaned = (
            #         name.replace("Kanwil", "")
            #             .replace("Kanca", "")
            #             .replace("Umum", "")
            #             .replace("Keuangan", "")
            #             .strip()
            #     )

            #     kanca = self.env['vit.kanca'].search([
            #         ('name', 'ilike', cleaned)
            #     ], limit=1)

            #     if kanca:
            #         user.write({'multi_kanca': [(4, kanca.id)]})

            #         if kanca.kanwil_id:
            #             user.write({'multi_kanwil': [(4, kanca.kanwil_id.id)]})

            if lower_name.startswith("kanwil") or lower_name.startswith("kanca"):

                cleaned = (
                    name.replace("Kanwil", "")
                        .replace("Kanca", "")
                        .replace("Umum", "")
                        .replace("Keuangan", "")
                        .strip()
                )

                # 1. CARI EXACT MATCH DULU (full name = "Kanca <cleaned>")
                exact_kanca_name = f"Kanca {cleaned}".strip()
                kanca = self.env['vit.kanca'].search([
                    ('name', '=', exact_kanca_name)
                ], limit=1)

                # 2. KALAU GA ADA EXACT, BARU fallback ke ILIKE (tapi sort yg paling pendek)
                if not kanca:
                    kanca_list = self.env['vit.kanca'].search([
                        ('name', 'ilike', cleaned),
                    ])
                    if kanca_list:
                        # pilih nama TERPENDEK = YANG PALING EXACT
                        kanca = sorted(kanca_list, key=lambda k: len(k.name))[0]

                # 3. SET ke user
                if kanca:
                    user.write({'multi_kanca': [(4, kanca.id)]})
                    if kanca.kanwil_id:
                        user.write({'multi_kanwil': [(4, kanca.kanwil_id.id)]})




        return users






    # kanca_id = fields.Many2one(
    #     'vit.kanca',
    #     string='Lokasi Kanca',
    # )

    # kanwil_id = fields.Many2one(
    #     'vit.kanwil', 
    #     string='Lokasi Kanwil Umum',
    # )

    # kanwil_keuangan_id = fields.Many2one(
    #     'vit.kanwil', 
    #     string='Lokasi Kanwil Keuangan',
    # )

    # is_kanca_group = fields.Boolean(
    #     string='Is Kanca Group',
    #     compute='_compute_is_kanca_group',
    # )


    # is_kanwil_group = fields.Boolean(
    #     string='Is Kanwil Group', 
    #     compute='_compute_is_kanwil_group'
    # )


    # is_kanwil_keuangan_group = fields.Boolean(
    #     string='Is Kanwil Keuangan Group',
    #     compute='_compute_is_kanwil_keuangan_group'
    # )


    # allowed_kanwil_id = fields.Many2one(
    #     'vit.kanwil', 
    #     string='Allowed Kanwil',
    # )

    # allowed_kanca_id = fields.Many2one(
    #     'vit.kanca',
    #     string='Allowed Kanca',
    # )

    # allowed_kanca_domain_ids = fields.Many2many(
    #     'vit.kanca',
    #     compute='_compute_allowed_kanca_domain',
    #     string='Allowed Kanca Domain',
    # )


    # is_allowed_kanca_group = fields.Boolean(
    #     string='Is Allowed Kanca Group',
    #     compute='_compute_is_allowed_kanca_group'
    # )

    # is_allowed_kanwil_group = fields.Boolean(
    #     string='Is Allowed Kanwil Group',
    #     compute='_compute_is_allowed_kanwil_group'
    # )


    # @api.depends('groups_id')
    # def _compute_is_kanca_group(self):
    #     for rec in self:
    #         rec.is_kanca_group = rec.has_group('vit_contract_inherit.group_vit_contract_kanca')
    #         if not rec.is_kanca_group:
    #             rec.kanca_id = False


    # @api.depends('groups_id')
    # def _compute_is_kanwil_group(self):
    #     for rec in self:
    #         rec.is_kanwil_group = rec.has_group('vit_contract_inherit.group_vit_contract_kanwil')
    #         if not rec.is_kanwil_group:
    #             rec.kanwil_id = False


    # @api.depends('groups_id')
    # def _compute_is_kanwil_keuangan_group(self):
    #     for rec in self:
    #         rec.is_kanwil_keuangan_group = rec.has_group('vit_contract_inherit.group_vit_contract_kanwil_keuangan')
    #         if not rec.is_kanwil_keuangan_group:
    #             rec.kanwil_keuangan_id = False



    # @api.depends('groups_id')
    # def _compute_is_allowed_kanca_group(self):
    #     for rec in self:
    #         has_allowed_kanca = rec.has_group('vit_contract_inherit.group_vit_contract_allowed_kanca')
    #         has_user = rec.has_group('vit_contract.group_vit_contract_user')
    #         rec.is_allowed_kanca_group = has_allowed_kanca and has_user
    #         if not rec.is_allowed_kanca_group:
    #             rec.allowed_kanca_id = False

    # @api.depends('groups_id')
    # def _compute_is_allowed_kanwil_group(self):
    #     for rec in self:
    #         has_allowed_kanwil = rec.has_group('vit_contract_inherit.group_vit_contract_allowed_kanwil')
    #         has_user = rec.has_group('vit_contract.group_vit_contract_user')
    #         rec.is_allowed_kanwil_group = has_allowed_kanwil and has_user
    #         if not rec.is_allowed_kanwil_group:
    #             rec.allowed_kanwil_id = False



    # @api.onchange('allowed_kanwil_id')
    # def _onchange_allowed_kanwil_id(self):
    #     """Reset allowed_kanca_id hanya jika allowed_kanwil_id benar-benar berubah ke yang lain."""
    #     for rec in self:
    #         if not rec._origin or not rec._origin.allowed_kanwil_id:
    #             continue
    #         old_kanwil = rec._origin.allowed_kanwil_id
    #         new_kanwil = rec.allowed_kanwil_id
    #         if old_kanwil and new_kanwil and old_kanwil.id != new_kanwil.id:
    #             rec.allowed_kanca_id = False
    #         elif not new_kanwil:
    #             rec.allowed_kanca_id = False
                


    # @api.depends('allowed_kanwil_id', 'groups_id')
    # def _compute_allowed_kanca_domain(self):
    #     for rec in self:
    #         domain = []
    #         if rec.has_group('vit_contract_inherit.group_vit_contract_allowed_kanwil'):
    #             if rec.allowed_kanwil_id:
    #                 domain = [('kanwil_id', '=', rec.allowed_kanwil_id.id)]
    #             else:
    #                 domain = [('id', '=', 0)] 
    #         elif rec.has_group('vit_contract_inherit.group_vit_contract_allowed_kanca'):
    #             domain = [] 
    #         else:
    #             domain = [('id', '=', 0)] 

    #         rec.allowed_kanca_domain_ids = self.env['vit.kanca'].search(domain)


    # @api.constrains('groups_id')
    # def _check_allowed_dependencies(self):
    #     for rec in self:
    #         errors = []

    #         has_user = rec.has_group('vit_contract.group_vit_contract_user')
    #         has_allowed_kanca = rec.has_group('vit_contract_inherit.group_vit_contract_allowed_kanca')
    #         has_allowed_kanwil = rec.has_group('vit_contract_inherit.group_vit_contract_allowed_kanwil')

    #         if (has_allowed_kanca or has_allowed_kanwil) and not has_user:
    #             if has_allowed_kanca and has_allowed_kanwil:
    #                 errors.append("Group 'Allowed Kanwil' dan 'Allowed Kanca' hanya bisa diaktifkan jika Group 'User' juga aktif.")
    #             elif has_allowed_kanca:
    #                 errors.append("Group 'Allowed Kanca' hanya bisa diaktifkan jika Group 'User' juga aktif.")
    #             elif has_allowed_kanwil:
    #                 errors.append("Group 'Allowed Kanwil' hanya bisa diaktifkan jika Group 'User' juga aktif.")

    #         if errors:
    #             raise ValidationError("\n".join(errors))