# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class UtilityContractInvoiceLine(models.Model):
    _name = "utility.contract_invoice_line"
    _description = "Utility Contract Invoice Line"
    _order = "sequence, id"

    @api.multi
    @api.depends(
        "contract_id",
    )
    def _compute_allowed_invoice_item_ids(self):
        for document in self:
            document.allowed_invoice_item_ids = False
            if document.contract_id:
                document.allowed_invoice_item_ids = (
                    document.contract_id.meter_id.type_id.allowed_invoice_item_ids.ids
                )

    @api.multi
    @api.depends(
        "item_id",
    )
    def _compute_qty_computation_method(self):
        for document in self:
            document.qty_computation_method = False
            if document.item_id:
                document.qty_computation_method = (
                    document.item_id.qty_computation_method
                )

    contract_id = fields.Many2one(
        string="# Contract",
        comodel_name="utility.contract",
        ondelete="cascade",
        copy=False,
    )
    allowed_invoice_item_ids = fields.Many2many(
        string="Allowed Utility Type",
        comodel_name="utility.contract_invoice_item",
        compute="_compute_allowed_invoice_item_ids",
        store=False,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=5,
    )
    item_id = fields.Many2one(
        string="Item",
        comodel_name="utility.contract_invoice_item",
        required=True,
    )
    qty_computation_method = fields.Selection(
        string="Qty Computation Method",
        selection=[
            ("manual", "Manual"),
            ("automatic", "Automatic"),
        ],
        compute="_compute_qty_computation_method",
        store=False,
    )
    qty = fields.Float(
        string="Qty",
    )
    tax_ids = fields.Many2many(
        string="Tax(es)",
        comodel_name="account.tax",
        relation="rel_contract_line_2_tax",
        column1="line_id",
        column2="tax_id",
    )

    @api.onchange(
        "item_id",
    )
    def onchange_tax_ids(self):
        self.tax_ids = False
        if self.item_id:
            self.tax_ids = self.item_id.product_id.taxes_id.ids

    @api.multi
    def _prepare_invoice_line(self, schedule):
        self.ensure_one()
        income_account = self._get_income_account()
        uom = self._get_uos()
        taxes = self._get_taxes()
        analytic = self._get_analytic()
        return {
            "name": self.item_id.name,
            "product_id": self.item_id.product_id.id,
            "account_id": income_account and income_account.id or False,
            "quantity": self._get_qty(schedule),
            "uos_id": uom and uom.id or False,
            "price_unit": self._get_price_unit(schedule),
            "invoice_line_tax_id": taxes,
            "account_analytic_id": analytic and analytic.id or False,
        }

    @api.multi
    def _get_analytic(self):
        self.ensure_one()
        return self.contract_id.analytic_account_id

    @api.multi
    def _get_income_account(self):
        self.ensure_one()
        return self.item_id.product_id.property_account_income

    @api.multi
    def _get_uos(self):
        self.ensure_one()
        return self.item_id.product_id.uom_id

    @api.multi
    def _get_taxes(self):
        self.ensure_one()
        return [(6, 0, self.tax_ids.ids)]

    @api.multi
    def _get_qty(self, schedule):
        self.ensure_one()
        if self.qty_computation_method == "manual":
            result = self.qty
        else:
            result = self.item_id._get_qty(self, schedule)
        return result

    @api.multi
    def _get_price_unit(self, schedule):
        self.ensure_one()
        contract = self.contract_id
        product = self.item_id.product_id
        if self.item_id.unit_price_computation_method == "default":
            result = contract.pricelist_id.price_get(
                prod_id=product.id, qty=self.qty or 1.0
            )[contract.pricelist_id.id]
        else:
            result = self.item_id._get_unit_price(self, schedule)
        return result
