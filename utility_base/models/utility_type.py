# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class UtilityType(models.Model):
    _name = "utility.type"
    _description = "Utility Type"

    name = fields.Char(
        string="Utility Type",
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    note = fields.Text(
        string="Note",
    )
    uom_category_id = fields.Many2one(
        string="UoM Category",
        comodel_name="product.uom.categ",
        required=True,
    )
    allowed_uom_ids = fields.Many2many(
        string="Allowed UoM(s)",
        comodel_name="product.uom",
        relation="rel_utility_type_2_uom",
        column1="type_id",
        column2="uom_id",
    )

    @api.onchange(
        "uom_category_id",
    )
    def onchange_allowed_uom_ids(self):
        self.allowed_uom_ids = False
