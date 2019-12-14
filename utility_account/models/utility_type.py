# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class UtilityType(models.Model):
    _name = "utility.type"
    _inherit = "utility.type"

    allowed_invoice_item_ids = fields.Many2many(
        string="Allowed Invoice Items",
        comodel_name="utility.contract_invoice_item",
        relation="rel_invoice_item_2_utility_type",
        column1="type_id",
        column2="item_id",
    )
