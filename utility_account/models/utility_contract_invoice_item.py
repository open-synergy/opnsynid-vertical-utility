# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools.safe_eval import safe_eval as eval


class UtilityContractInvoiceItem(models.Model):
    _name = "utility.contract_invoice_item"
    _description = "Utility Contract Invoice Item"

    name = fields.Char(
        string="Item",
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
    product_id = fields.Many2one(
        string="Product Link",
        comodel_name="product.product",
        required=True,
    )
    allowed_utility_type_ids = fields.Many2many(
        string="Allowed Utility Type",
        comodel_name="utility.type",
        relation="rel_invoice_item_2_utility_type",
        column1="item_id",
        column2="type_id",
    )
    default_sequence = fields.Integer(
        string="Default Sequence",
        required=True,
        default=5,
    )
    qty_computation_method = fields.Selection(
        string="Qty Computation Method",
        selection=[
            ("manual", "Manual"),
            ("automatic", "Automatic"),
        ],
        required=True,
        default="manual",
    )
    python_code_qty = fields.Text(
        string="Python Code for Qty Computation",
        default="result = 0.0",
    )
    unit_price_computation_method = fields.Selection(
        string="Unit Price Computation Method",
        selection=[
            ("default", "Manual"),
            ("automatic", "Automatic"),
        ],
        required=True,
        default="default",
    )
    python_code_unit_price = fields.Text(
        string="Python Code for Unit Price Computation",
        default="result = 0.0",
    )
    note = fields.Text(
        string="Note",
    )

    def _get_localdict(self, document):
        self.ensure_one()
        return {
            "env": self.env,
            "document": document,
        }

    @api.multi
    def _get_qty(self, document):
        self.ensure_one()
        localdict = self._get_localdict(document)
        try:
            eval(self.python_code_qty,
                 localdict, mode="exec", nocopy=True)
            result = localdict["result"]
        except:  # noqa: E722
            result = 0.0
        return result

    @api.multi
    def _get_unit_price(self, document):
        self.ensure_one()
        result = 0.0
        localdict = self._get_localdict(document)
        try:
            eval(self.python_code_unit_price,
                 localdict, mode="exec", nocopy=True)
            result = localdict["result"]
        except:  # noqa: E722
            result = 0.0
        return result
