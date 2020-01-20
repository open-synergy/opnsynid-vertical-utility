# -*- coding: utf-8 -*-
# Copyright 2019-2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class UtilityContractInvoiceSchedule(models.Model):
    _name = "utility.contract_invoice_schedule"
    _description = "Utility Contract Invoice Schedule"
    _order = "schedule_date, id"

    @api.multi
    @api.depends(
        "contract_id",
        "contract_id.state",
    )
    def _compute_contract_state(self):
        for document in self:
            document.contract_state = document.contract_id.state

    @api.multi
    @api.depends(
        "manual",
        "invoice_id",
        "invoice_id.state",
    )
    def _compute_state(self):
        for document in self:
            state = "uninvoiced"
            if document.manual:
                state = "done"
            elif document.invoice_id and document.invoice_id.state == "open":
                state = "invoiced"
            elif document.invoice_id and document.invoice_id.state == "paid":
                state = "done"
            document.state = state

    contract_id = fields.Many2one(
        string="# Contract",
        comodel_name="utility.contract",
        ondelete="cascade",
        copy=False,
    )
    meter_id = fields.Many2one(
        string="# Meter",
        related="contract_id.meter_id",
        comodel_name="utility.meter",
        store=True,
    )
    partner_id = fields.Many2one(
        string="Customer",
        related="contract_id.partner_id",
        comodel_name="res.partner",
        store=True,
    )
    period_start_date = fields.Date(
        string="Period Start Date",
        required=True,
    )
    schedule_date = fields.Date(
        string="Schedule Date",
        required=True,
        copy=False,
    )
    invoice_id = fields.Many2one(
        string="# Invoice",
        comodel_name="account.invoice",
        ondelete="restrict",
    )
    manual = fields.Boolean(
        string="Manually Controlled",
        readonly=True,
    )
    meter_reading_ids = fields.One2many(
        string="Meter Readings",
        comodel_name="utility.meter_reading",
        inverse_name="schedule_id",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("uninvoiced", "Uninvoiced"),
            ("invoiced", "Invoiced"),
            ("done", "Paid/Done"),
        ],
        compute="_compute_state",
        store=True,
    )
    contract_state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("approve", "Ready To Start"),
            ("open", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("terminate", "Terminate"),
        ],
        compute="_compute_contract_state",
    )

    @api.multi
    def action_generate_invoice(self):
        for document in self:
            document._attach_meter_reading()
            document._generate_invoice()

    @api.multi
    def action_reset_invoice(self):
        for document in self:
            document._reset_invoice()

    @api.multi
    def action_uncontrol_schedule(self):
        for document in self:
            document.write(document._prepare_uncontrol_schedule())

    @api.multi
    def action_control_schedule(self):
        for document in self:
            document.write(document._prepare_control_schedule())

    @api.multi
    def _prepare_uncontrol_schedule(self):
        self.ensure_one()
        return {
            "manual": True,
        }

    @api.multi
    def _prepare_control_schedule(self):
        self.ensure_one()
        return {
            "manual": False,
        }

    @api.multi
    def _generate_invoice(self):
        self.ensure_one()
        self.write(self._prepare_generate_invoice_data())

    @api.multi
    def _reset_invoice(self):
        self.ensure_one()
        inv = self.invoice_id
        self.write(self._prepare_reset_invoice_data())
        inv.unlink()

    @api.multi
    def _prepare_reset_invoice_data(self):
        self.ensure_one()
        return {
            "invoice_id": False,
        }

    @api.multi
    def _prepare_generate_invoice_data(self):
        self.ensure_one()
        invoice = self._create_invoice()
        return {
            "invoice_id": invoice.id
        }

    @api.multi
    def _create_invoice(self):
        self.ensure_one()
        obj_invoice = self.env["account.invoice"]
        return obj_invoice.create(self._prepare_create_invoice_data())

    @api.multi
    def _prepare_create_invoice_data(self):
        self.ensure_one()
        journal = self._get_journal() or False
        account = self._get_account_receivable() or False
        payment_term = self._get_payment_term() or False
        lines = self._get_invoice_lines()
        contract = self.contract_id
        template = contract.template_id
        bank = self._get_bank_account()
        return {
            "partner_id": contract.partner_id.id,
            "origin": contract.name,
            "type": "out_invoice",
            "journal_id": journal and journal.id or False,
            "account_id": account and account.id or False,
            "date_invoice": self.schedule_date,
            "payment_term": payment_term and payment_term.id or False,
            "invoice_line": lines,
            "name": template._get_invoice_description(self),
            "partner_bank_id": bank and bank.id or False,
        }

    @api.multi
    def _get_journal(self):
        self.ensure_one()
        result = False
        contract = self.contract_id
        if contract:
            result = contract.journal_id
        return result

    @api.multi
    def _get_bank_account(self):
        self.ensure_one()
        result = False
        contract = self.contract_id
        if contract:
            result = contract.bank_account_id
        return result

    @api.multi
    def _get_account_receivable(self):
        self.ensure_one()
        result = False
        contract = self.contract_id
        if contract:
            result = contract.account_receivable_id
        return result

    @api.multi
    def _get_payment_term(self):
        self.ensure_one()
        result = False
        contract = self.contract_id
        if contract:
            result = contract.payment_term_id
        return result

    @api.multi
    def _get_invoice_lines(self):
        self.ensure_one()
        result = []
        for invoice_item in self.contract_id.invoice_item_ids:
            result.append((0, 0, invoice_item._prepare_invoice_line(self)))
        return result

    @api.multi
    def _attach_meter_reading(self):
        self.ensure_one()
        criteria = self._prepare_meter_reading_domain()
        obj_reading = self.env["utility.meter_reading"]
        obj_reading.search(criteria).write({"schedule_id": self.id})

    @api.multi
    def _prepare_meter_reading_domain(self):
        self.ensure_one()
        date_max = self.schedule_date + " 00:00:00"
        return [
            ("schedule_id", "=", False),
            ("date_reading_tz", "<=", date_max)
        ]

    @api.multi
    def unlink(self):
        strWarning = _("You can only delete schedule with no invoice")
        for document in self:
            if document.invoice_id:
                if not self.env.context.get("force_unlink", False):
                    raise UserError(strWarning)
        _super = super(UtilityContractInvoiceSchedule, self)
        _super.unlink()

    @api.model
    def cron_create_invoice(self):
        today = fields.Date.today()
        obj_schedule = self.env["utility.contract_invoice_schedule"]
        criteria = [
            ("schedule_date", "=", today),
            ("state", "=", "uninvoiced"),
            ("contract_id.state", "=", "open"),
        ]
        schedules = obj_schedule.search(criteria)
        schedules.action_generate_invoice()
