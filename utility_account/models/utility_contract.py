# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)

try:
    import pandas as pd
except (ImportError, IOError) as err:
    _logger.debug(err)


class UtilityContract(models.Model):
    _name = "utility.contract"
    _description = "Utility Contract"
    _inherit = [
        "mail.thread",
        "base.sequence_document",
        "base.workflow_policy_object",
        "base.cancel.reason_common",
        "base.terminate.reason_common",
    ]

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.model
    def _default_user_id(self):
        return self.env.user.id

    @api.multi
    def _compute_policy(self):
        _super = super(UtilityContract, self)
        _super._compute_policy()

    @api.multi
    @api.depends(
        "schedule_ids",
        "schedule_ids.schedule_date",
    )
    def _compute_last_invoice_date(self):
        for document in self:
            document.last_invoice_date = False
            if document.schedule_ids:
                last_schedule = document.schedule_ids[-1]
                document.last_invoice_date = last_schedule.schedule_date

    name = fields.Char(
        string="# Document",
        default="/",
        required=True,
        copy=False,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_start = fields.Date(
        string="Date Start",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_end = fields.Date(
        string="Date End",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
    )
    user_id = fields.Many2one(
        string="Responsible",
        comodel_name="res.users",
        default=lambda self: self._default_user_id(),
        help="Person who responsible to this contract",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    template_id = fields.Many2one(
        string="Template",
        comodel_name="utility.contract_template",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    pricelist_id = fields.Many2one(
        string="Pricelist",
        comodel_name="product.pricelist",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    bank_account_id = fields.Many2one(
        string="Bank Account",
        comodel_name="res.partner.bank",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    account_receivable_id = fields.Many2one(
        string="Account Receivable",
        comodel_name="account.account",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    payment_term_id = fields.Many2one(
        string="Payment Term",
        comodel_name="account.payment.term",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    first_invoice_date = fields.Date(
        string="First Invoice Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    last_invoice_date = fields.Date(
        string="Last Invoice Date",
        compute="_compute_last_invoice_date",
        store=True,
    )
    period = fields.Selection(
        string="Period",
        selection=[
            ("D", "Daily"),
            ("MS", "Monthly"),
            ("YS", "Yearly"),
        ],
        default="MS",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    period_number = fields.Integer(
        string="Period Number",
        default=1,
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    schedule_ids = fields.One2many(
        string="Schedule",
        comodel_name="utility.contract_invoice_schedule",
        inverse_name="contract_id",
        readonly=True,
    )
    invoice_item_ids = fields.One2many(
        string="Invoice Items",
        comodel_name="utility.contract_invoice_line",
        inverse_name="contract_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    note = fields.Text(
        string="Note",
    )
    state = fields.Selection(
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
        default="draft",
        required=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        string="Customer",
        comodel_name="res.partner",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    analytic_account_id = fields.Many2one(
        string="Analytic Account",
        comodel_name="account.analytic.account",
        readonly=True,
        required=False,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    meter_id = fields.Many2one(
        string="Meter",
        comodel_name="utility.meter",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    # Policy Field
    confirm_ok = fields.Boolean(
        string="Can Confirm",
        compute="_compute_policy",
    )
    approve_ok = fields.Boolean(
        string="Can Approve",
        compute="_compute_policy",
    )
    start_ok = fields.Boolean(
        string="Can Start",
        compute="_compute_policy",
    )
    done_ok = fields.Boolean(
        string="Can Finish",
        compute="_compute_policy",
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
    )
    restart_ok = fields.Boolean(
        string="Can Restart",
        compute="_compute_policy",
    )
    terminate_ok = fields.Boolean(
        string="Can Terminate",
        compute="_compute_policy",
    )

    # Log Fields
    confirm_date = fields.Datetime(
        string="Confirm Date",
        readonly=True,
    )
    confirm_user_id = fields.Many2one(
        string="Confirmed By",
        comodel_name="res.users",
        readonly=True,
    )
    approve_date = fields.Datetime(
        string="Approve Date",
        readonly=True,
    )
    approve_user_id = fields.Many2one(
        string="Approve By",
        comodel_name="res.users",
        readonly=True,
    )
    start_user_id = fields.Many2one(
        string="Start By",
        comodel_name="res.users",
        readonly=True,
    )
    start_date = fields.Datetime(
        string="Start Date",
        readonly=True,
    )
    done_date = fields.Datetime(
        string="Finish Date",
        readonly=True,
    )
    done_user_id = fields.Many2one(
        string="Finished By",
        comodel_name="res.users",
        readonly=True,
    )
    cancel_date = fields.Datetime(
        string="Cancel Date",
        readonly=True,
    )
    cancel_user_id = fields.Many2one(
        string="Cancelled By",
        comodel_name="res.users",
        readonly=True,
    )
    terminate_date = fields.Datetime(
        string="Terminate Date",
        readonly=True,
    )
    terminate_user_id = fields.Many2one(
        string="Terminate By",
        comodel_name="res.users",
        readonly=True,
    )

    @api.onchange(
        "partner_id",
    )
    def onchange_meter_id(self):
        self.meter_id = False

    @api.onchange(
        "template_id",
        "company_id",
    )
    def onchange_bank_account_id(self):
        self.bank_account_id = False
        if self.template_id:
            self.bank_account_id = self.template_id.default_bank_account_id

    @api.onchange(
        "template_id",
    )
    def onchange_journal_id(self):
        self.journal_id = False
        if self.template_id:
            self.journal_id = self.template_id.default_journal_id

    @api.onchange(
        "template_id",
    )
    def onchange_receivable_account_id(self):
        self.account_receivable_id = False
        if self.template_id:
            self.account_receivable_id = self.template_id.default_receivable_account_id

    @api.onchange(
        "template_id",
    )
    def onchange_payment_term_id(self):
        self.payment_term_id = False
        if self.template_id:
            self.payment_term_id = self.template_id.default_payment_term_id

    @api.multi
    def action_confirm(self):
        for document in self:
            document.write(document._prepare_confirm_data())

    @api.multi
    def action_approve(self):
        for document in self:
            document.write(document._prepare_approve_data())

    @api.multi
    def action_start(self):
        for document in self:
            document.write(document._prepare_start_data())

    @api.multi
    def action_done(self):
        for document in self:
            document.write(document._prepare_done_data())

    @api.multi
    def action_cancel(self):
        for document in self:
            document.write(document._prepare_cancel_data())
            document._clear_schedule()

    @api.multi
    def action_restart(self):
        for document in self:
            document.write(document._prepare_restart_data())

    @api.multi
    def action_terminate(self):
        for document in self:
            document.write(document._prepare_terminate_data())

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        return {
            "state": "confirm",
            "confirm_date": fields.Datetime.now(),
            "confirm_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_approve_data(self):
        self.ensure_one()
        return {
            "state": "approve",
            "approve_date": fields.Datetime.now(),
            "approve_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_start_data(self):
        self.ensure_one()
        return {
            "state": "open",
            "start_date": fields.Datetime.now(),
            "start_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_done_data(self):
        self.ensure_one()
        return {
            "state": "done",
            "done_date": fields.Datetime.now(),
            "done_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        return {
            "state": "cancel",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
        }

    @api.multi
    def _prepare_restart_data(self):
        self.ensure_one()
        return {
            "state": "draft",
            "confirm_date": False,
            "confirm_user_id": False,
            "approve_date": False,
            "approve_user_id": False,
            "start_date": False,
            "start_user_id": False,
            "done_date": False,
            "done_user_id": False,
            "cancel_date": False,
            "cancel_user_id": False,
            "terminate_date": False,
            "terminate_user_id": False,
        }

    @api.multi
    def _prepare_terminate_data(self):
        self.ensure_one()
        return {
            "state": "terminate",
            "terminate_date": fields.Datetime.now(),
            "terminate_user_id": self.env.user.id,
        }

    @api.multi
    def action_generate_schedule(self):
        for document in self:
            document._generate_schedule()

    @api.multi
    def _generate_schedule(self):
        self.ensure_one()

        if self.schedule_ids:
            self._clear_schedule()

        obj_schedule = self.env["utility.contract_invoice_schedule"]
        pd_schedule = self._get_schedule()
        dt_period = datetime.strptime(self.first_invoice_date, "%Y-%m-%d")
        dt_period_date_start = datetime.strptime(self.date_start, "%Y-%m-%d")
        offset = dt_period.day
        for period in range(0, self.period_number):
            obj_schedule.create(
                {
                    "contract_id": self.id,
                    "schedule_date": dt_period.strftime("%Y-%m-%d"),
                    "period_start_date": dt_period_date_start.strftime("%Y-%m-%d"),
                }
            )
            dt_period_date_start = dt_period
            dt_period = pd_schedule[period] + pd.DateOffset(day=offset)

    @api.multi
    def _get_schedule(self):
        self.ensure_one()
        return pd.date_range(
            start=self.first_invoice_date,
            periods=self.period_number,
            freq=self.period,
        ).to_pydatetime()

    @api.multi
    def _clear_schedule(self):
        self.ensure_one()
        invoices = self.env["account.invoice"]
        for schedule in self.schedule_ids:
            if schedule.invoice_id:
                invoices += schedule.invoice_id
        self.schedule_ids.write({"invoice_id": False})
        self.schedule_ids.unlink()
        invoices.unlink()

    @api.multi
    def unlink(self):
        strWarning = _("You can only delete data on draft state")
        for document in self:
            if document.state != "draft":
                if not self.env.context.get("force_unlink", False):
                    raise UserError(strWarning)
        _super = super(UtilityContract, self)
        _super.unlink()

    @api.model
    def create(self, values):
        _super = super(UtilityContract, self)
        result = _super.create(values)
        sequence = result._create_sequence()
        result.write(
            {
                "name": sequence,
            }
        )
        return result

    @api.constrains("date_start", "date_end")
    def _check_real_date(self):
        strWarning = _("Date End must be " "greater than Date Start")
        for document in self:
            if document.date_start and document.date_end:
                if document.date_start > document.date_end:
                    raise UserError(strWarning)

    @api.constrains("date_start", "first_invoice_date")
    def _check_first_invoice_date(self):
        strWarning = _("First Invoice Date must be " "greater than Date Start")
        for document in self:
            if document.date_start and document.first_invoice_date:
                if document.date_start > document.first_invoice_date:
                    raise UserError(strWarning)

    @api.constrains(
        "date_end",
        "last_invoice_date",
        "state",
    )
    def _check_last_invoice_date(self):
        strWarning = _("Last Invoice Date must be " "greater or equal than Date End")
        for document in self:
            if (
                document.date_end
                and document.last_invoice_date
                and document.state != "draft"
            ):
                if document.date_end > document.last_invoice_date:
                    raise UserError(strWarning)

    @api.constrains(
        "schedule_ids",
        "state",
    )
    def _check_invoice_schedule(self):
        warning_msg = _("Please create invoice schedule")
        for document in self:
            if document.state != "draft" and len(document.schedule_ids) == 0:
                raise UserError(warning_msg)

    @api.constrains(
        "schedule_ids",
        "state",
    )
    def _check_invoice_line(self):
        warning_msg = _("Please create invoice line")
        for document in self:
            if document.state != "draft" and len(document.invoice_item_ids) == 0:
                raise UserError(warning_msg)

    @api.constrains(
        "state",
    )
    def _check_schedule_state(self):
        warning_msg = _("Schedule has to be paid/done")
        obj_schedule = self.env["utility.contract_invoice_schedule"]
        for document in self:
            criteria = [
                ("contract_id", "=", document.id),
                ("state", "!=", "done"),
            ]
            unfinish_count = obj_schedule.search_count(criteria)
            if document.state == "done" and unfinish_count != 0:
                raise UserError(warning_msg)
