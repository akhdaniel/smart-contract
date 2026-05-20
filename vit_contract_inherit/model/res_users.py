import base64
import io

from PIL import Image, ImageDraw, ImageFont

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    entity_initials = fields.Char(
        string='Entity Initials',
        compute='_compute_entity_initials',
        store=True,
        readonly=True,
        help='Singkatan entitas untuk tampilan profil, mis. Sumatera Utara -> SU.',
    )
    entity_avatar_html = fields.Html(
        string='Entity Avatar',
        compute='_compute_entity_avatar_html',
        sanitize=False,
    )
    entity_avatar_generated = fields.Boolean(
        string='Entity Avatar Generated',
        default=False,
    )
    entity_avatar_manual = fields.Boolean(
        string='Entity Avatar Manual',
        default=False,
        help='Menandai bahwa avatar diunggah manual sehingga tidak ditimpa avatar entitas.',
    )

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

    @api.depends('name', 'multi_kanwil.name', 'multi_kanca.name')
    def _compute_entity_initials(self):
        ignored_words = {'kanwil', 'kanca', 'keuangan', 'umum'}

        def _build_initials(source_name):
            words = [word for word in (source_name or '').replace('-', ' ').split() if word]
            filtered_words = [word for word in words if word.lower() not in ignored_words]
            target_words = filtered_words or words

            if not target_words:
                return False

            if len(target_words) == 1:
                return target_words[0][:2].upper()

            return ''.join(word[0].upper() for word in target_words[:3])

        for rec in self:
            source_name = False
            if rec.multi_kanca:
                source_name = rec.multi_kanca[0].name
            elif rec.multi_kanwil:
                source_name = rec.multi_kanwil[0].name
            else:
                source_name = rec.name

            rec.entity_initials = _build_initials(source_name)

    @api.depends('entity_initials')
    def _compute_entity_avatar_html(self):
        for rec in self:
            initials = (rec.entity_initials or '?').upper()
            bg_color = rec._get_entity_avatar_color(initials)
            rec.entity_avatar_html = """
                <div style="
                    width: 84px;
                    height: 84px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-color: %s;
                    color: #FFFFFF;
                    font-size: 32px;
                    font-weight: 600;
                    border-radius: 0;
                    margin-left: auto;
                    text-transform: uppercase;
                ">%s</div>
            """ % (bg_color, initials)

    def _get_entity_avatar_color(self, initials):
        colors = [
            '#875A7B',
            '#C78516',
            '#2C8397',
            '#3B7E3E',
            '#7A4F01',
            '#5E5E5E',
        ]
        color_index = sum(ord(char) for char in (initials or '')) % len(colors)
        return colors[color_index]

    def _generate_entity_avatar_image(self, initials):
        initials = (initials or '?').upper()
        bg_color = self._get_entity_avatar_color(initials)

        image = Image.new('RGB', (256, 256), bg_color)
        draw = ImageDraw.Draw(image)

        font = None
        for font_name in ['DejaVuSans-Bold.ttf', 'arialbd.ttf', 'Arial Bold.ttf']:
            try:
                font = ImageFont.truetype(font_name, 110)
                break
            except Exception:
                continue
        if not font:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = (
            (256 - text_width) / 2,
            (256 - text_height) / 2 - 8,
        )
        draw.text(position, initials, fill='white', font=font)

        output = io.BytesIO()
        image.save(output, format='PNG')
        return base64.b64encode(output.getvalue())

    def _sync_entity_avatar(self, force=False):
        for rec in self:
            if not rec.partner_id or not rec.entity_initials:
                continue
            if rec.entity_avatar_manual and not force:
                continue

            avatar_image = rec._generate_entity_avatar_image(rec.entity_initials)
            vals = {
                'image_1920': avatar_image,
                'entity_avatar_generated': True,
                'entity_avatar_manual': False,
            }
            super(ResUsers, rec).write(vals)
            rec.partner_id.sudo().write({'image_1920': avatar_image})

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

            if user.partner_id and vals.get('login'):
                user.partner_id.email = vals['login']

            name = vals.get('name', '').strip()
            if not name:
                continue

            lower_name = name.lower()

            # =====================================================
            # 1. SPECIAL CASE: Kanwil Umum
            # =====================================================
            if lower_name.startswith("kanwil umum"):

                cleaned = (
                    name.replace("Kanwil", "")
                        .replace("Umum", "")
                        .strip()
                )

                kanwil = self.env['vit.kanwil'].search([
                    ('name', 'ilike', cleaned)
                ], limit=1)

                if kanwil:
                    user.write({'multi_kanwil': [(4, kanwil.id)]})

                continue

            # =====================================================
            # 2. SPECIAL CASE: Kanwil Keuangan
            # =====================================================
            if lower_name.startswith("kanwil keuangan"):

                cleaned = (
                    name.replace("Kanwil", "")
                        .replace("Keuangan", "")
                        .strip()
                )

                kanwil = self.env['vit.kanwil'].search([
                    ('name', 'ilike', cleaned)
                ], limit=1)

                if kanwil:
                    user.write({'multi_kanwil': [(4, kanwil.id)]})

                continue



            # =====================================================
            # 3. Selain itu → dianggap KANCA
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

                exact_kanca_name = f"Kanca {cleaned}".strip()
                kanca = self.env['vit.kanca'].search([
                    ('name', '=', exact_kanca_name)
                ], limit=1)

                if not kanca:
                    kanca_list = self.env['vit.kanca'].search([
                        ('name', 'ilike', cleaned),
                    ])
                    if kanca_list:
                        kanca = sorted(kanca_list, key=lambda k: len(k.name))[0]

                if kanca:
                    user.write({'multi_kanca': [(4, kanca.id)]})
                    if kanca.kanwil_id:
                        user.write({'multi_kanwil': [(4, kanca.kanwil_id.id)]})

        users._sync_entity_avatar(force=True)

        return users

    def write(self, vals):
        image_updated = 'image_1920' in vals
        manual_image = bool(vals.get('image_1920')) if image_updated else False

        if manual_image:
            vals['entity_avatar_generated'] = False
            vals['entity_avatar_manual'] = True
        elif image_updated:
            vals['entity_avatar_manual'] = False

        result = super().write(vals)

        tracked_fields = {'name', 'multi_kanwil', 'multi_kanca', 'image_1920'}
        if tracked_fields.intersection(vals.keys()) and not manual_image:
            force = image_updated and not vals.get('image_1920')
            self._sync_entity_avatar(force=force)

        return result


    # @api.model
    # def create(self, vals):
    #     user = super().create(vals)
    #     if user.partner_id and vals.get('login'):
    #         user.partner_id.email = vals['login']
    #     return user


# 
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
