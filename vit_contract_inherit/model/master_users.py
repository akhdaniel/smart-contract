from odoo import models, fields, api, _
from odoo.exceptions import UserError


class master_users(models.Model):
    _inherit = "vit.master_users"
    _order = "users_name asc"

    name = fields.Char(required=False, copy=False, string=_("Nama Vendor"))
    users_name = fields.Char(required=True, string=_("Username"))
    email = fields.Char(required=True, string=_("Email"))
    street = fields.Char(required=True, string=_("Alamat"))
    phone = fields.Char(required=True, string=_("Nomor Telepon"))
    password = fields.Char(required=True, string=_("Password"))
    created_user_id = fields.Many2one("res.users", string="Linked User", readonly=True)

    def action_create_user(self):
        for record in self:
            if not record.email:
                raise UserError(_("Isi dulu kolom 'Email'"))
            if not record.password:
                raise UserError(_("Isi dulu kolom 'Password'"))

            existing_user = self.env["res.users"].search(
                [("login", "=", record.email.lower().strip())], limit=1
            )
            if existing_user:
                raise UserError(_("User dengan email ini sudah ada!"))

            vendor_group = self.env.ref(
                "vit_contract_inherit.group_vit_contract_vendor", raise_if_not_found=False
            )
            if not vendor_group:
                raise UserError(_("Group Vendor tidak ditemukan!"))

            user_vals = {
                "name": record.name or record.users_name,
                "login": record.email.lower().strip(),
                "email": record.email.lower().strip(),
                "street": record.street,
                "phone": record.phone,
                "password": record.password,
            }

            user = self.env["res.users"].create(user_vals)
            user.write({"groups_id": [(4, vendor_group.id)]})

            record.created_user_id = user.id




    def unlink(self):
        """Kalau Master User dihapus, user Odoo-nya ikut dihapus."""
        for record in self:
            if record.created_user_id:
                record.created_user_id.sudo().unlink()
        return super(master_users, self).unlink()























# from odoo import models, fields, api, _
# from odoo.exceptions import UserError

# class master_users(models.Model):

#     _inherit = "vit.master_users"
#     _order = "users_id asc"


#     def action_reload_view(self):
#         pass

#     name = fields.Char( required=False, copy=False, string=_("Nama Vendor"))

#     users_id = fields.Many2one(comodel_name="res.users",  string=_("Users"), ondelete='cascade',)

#     user_groups_ids = fields.Many2many(
#         comodel_name="res.groups",
#         related="users_id.groups_id",
#         string="User Groups",
#         readonly=True,
#     )

#     @api.model
#     def create(self, vals):
#         record = super().create(vals)

#         vendor_group = self.env.ref("vit_contract_inherit.group_vit_contract_vendor", raise_if_not_found=False)
#         if not vendor_group:
#             raise ValueError(_("Group Vendor tidak ditemukan!"))

#         if not record.users_id:
#             login = (record.name or "").lower().replace(" ", "")
#             user_vals = {
#                 "name": record.name,
#                 "login": login,
#             }
#             user = self.env["res.users"].with_context(no_reset_password=True).create(user_vals)
#             user.write({"groups_id": [(4, vendor_group.id)]})
#             record.users_id = user.id
#         else:
#             record.users_id.write({"groups_id": [(4, vendor_group.id)]})

#         return record


    

    # @api.model
    # def create(self, vals):
    #     record = super().create(vals)

    #     vendor_group = self.env.ref("vit_contract_inherit.group_vit_contract_vendor", raise_if_not_found=False)
    #     if not vendor_group:
    #         raise ValueError(_("Group Vendor tidak ditemukan!"))

    #     if not record.users_id:
    #         login = (record.name or "").lower().replace(" ", "")
    #         user_vals = {
    #             "name": record.name,
    #             "login": login,
    #             "password": "12345",
    #         }
    #         user = self.env["res.users"].with_context(no_reset_password=True).create(user_vals)
    #         user.write({"groups_id": [(4, vendor_group.id)]})
    #         record.users_id = user.id
    #     else:
    #         record.users_id.write({"groups_id": [(4, vendor_group.id)]})

    #     return record