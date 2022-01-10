# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


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
    allowed_multiplier_item_ids = fields.Many2many(
        string="Allowed Multiplier Item",
        comodel_name="utility.meter_reading_multiplier_item",
        relation="rel_multiplier_item_2_utility_type",
        column1="type_id",
        column2="item_id",
        readonly=True,
    )
    multiplier_ids = fields.One2many(
        string="Multiplier Items",
        comodel_name="utility.type_multiplier",
        inverse_name="type_id",
    )

    @api.onchange(
        "uom_category_id",
    )
    def onchange_allowed_uom_ids(self):
        self.allowed_uom_ids = False
