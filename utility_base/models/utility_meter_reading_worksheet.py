# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil import relativedelta
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class UtilityMeterReadingWorksheet(models.Model):
    _name = "utility.meter_reading_worksheet"
    _inherit = [
        "mail.thread",
        "base.sequence_document",
        "base.workflow_policy_object",
        "base.cancel.reason_common",
    ]
    _description = "Utility Meter Reading Worksheet"

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    @api.model
    def _default_user_id(self):
        return self.env.user.id

    @api.multi
    def _compute_policy(self):
        _super = super(UtilityMeterReadingWorksheet, self)
        _super._compute_policy()

    name = fields.Char(
        string="# Document",
        default="/",
        help="""Document number

Leave / to assign automatic document number.
Automatic document number will be assign when data created.
Change / to assign document number manually.
        """,
        required=True,
        copy=False,
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
    template_id = fields.Many2one(
        string="Template",
        comodel_name="utility.meter_reading_worksheet_template",
        required=True,
        help="Worksheet template",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    scheduled_date_start = fields.Datetime(
        string="Scheduled Date Start",
        required=True,
        help="Measurement schedule date start",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    scheduled_date_end = fields.Datetime(
        string="Scheduled Date End",
        required=True,
        help="Measurement schedule date end",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    real_date_start = fields.Datetime(
        string="Real Date Start",
        readonly=True,
        help="Measurement real date start",
    )
    real_date_end = fields.Datetime(
        string="Real Date End",
        readonly=True,
        help="Measurement real date start",
    )
    user_id = fields.Many2one(
        string="Responsible",
        comodel_name="res.users",
        default=lambda self: self._default_user_id(),
        help="Person who responsible to take the measurement",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    meter_reading_ids = fields.One2many(
        string="Meter Readings",
        comodel_name="utility.meter_reading",
        inverse_name="worksheet_id",
        readonly=True,
        states={
            "open": [
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
        ],
        default="draft",
        required=True,
        readonly=True,
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

    @api.constrains("scheduled_date_start", "scheduled_date_end")
    def _check_scheduled_date(self):
        strWarning = _("Scheduled date end must be " "greater than scheduled date end")
        if self.scheduled_date_start and self.scheduled_date_end:
            if self.scheduled_date_start >= self.scheduled_date_end:
                raise UserError(strWarning)

    @api.constrains("real_date_start", "real_date_end")
    def _check_real_date(self):
        strWarning = _("Real date end must be " "greater than real date end")
        if self.real_date_start and self.real_date_end:
            if self.real_date_start >= self.real_date_end:
                raise UserError(strWarning)

    @api.multi
    def action_confirm(self):
        for document in self:
            document.write(document._prepare_confirm_data())

    @api.multi
    def action_approve(self):
        for document in self:
            document.write(document._prepare_approve_data())

    @api.multi
    def action_start(self, date_start=False):
        for document in self:
            document.write(document._prepare_start_data(date_start))

    @api.multi
    def action_done(self, date_end=False):
        for document in self:
            document.write(document._prepare_done_data())
            document.meter_reading_ids.action_valid()

    @api.multi
    def action_cancel(self):
        for document in self:
            document.write(document._prepare_cancel_data())
            document.meter_reading_ids.action_draft()

    @api.multi
    def action_restart(self):
        for document in self:
            document.write(document._prepare_restart_data())

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
            "meter_reading_ids": self._prepare_meter_readings(),
        }

    @api.multi
    def _prepare_start_data(self, date_start=False):
        self.ensure_one()
        real_date_start = date_start or fields.Datetime.now()
        return {
            "state": "open",
            "start_date": fields.Datetime.now(),
            "start_user_id": self.env.user.id,
            "real_date_start": real_date_start,
        }

    @api.multi
    def _prepare_done_data(self, date_end=False):
        self.ensure_one()
        real_date_end = date_end or fields.Datetime.now()
        return {
            "state": "done",
            "done_date": fields.Datetime.now(),
            "done_user_id": self.env.user.id,
            "real_date_end": real_date_end,
        }

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        return {
            "state": "cancel",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
            "real_date_start": False,
            "real_date_end": False,
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
        }

    @api.multi
    def _prepare_meter_readings(self):
        self.ensure_one()
        result = []
        template_meters = self.template_id.meter_ids
        worksheet_meters = self._get_existing_meters()
        meters_to_add = template_meters - worksheet_meters
        for meter in meters_to_add:
            result.append(
                (
                    0,
                    0,
                    {
                        "worksheet_id": self.id,
                        "meter_id": meter.id,
                    },
                )
            )
        meters_to_remove = worksheet_meters - template_meters
        self.meter_reading_ids.filtered(
            lambda r: r.meter_id.id in meters_to_remove.ids
        ).unlink()
        return result

    @api.multi
    def _get_existing_meters(self):
        self.ensure_one()
        result = self.env["utility.meter"]
        for meters in self.meter_reading_ids:
            result += meters.meter_id
        return result

    @api.model
    def create(self, values):
        _super = super(UtilityMeterReadingWorksheet, self)
        result = _super.create(values)
        sequence = result._create_sequence()
        result.write(
            {
                "name": sequence,
            }
        )
        return result

    @api.onchange(
        "template_id",
    )
    def onchange_user_id(self):
        self.user_id = False
        if self.template_id and self.template_id.default_user_id:
            self.user_id = self.template_id.default_user_id.id

    @api.onchange(
        "scheduled_date_start",
    )
    def onchange_schedule_date_end(self):
        self.scheduled_date_end = False
        if self.template_id:
            dt_start = datetime.strptime(self.scheduled_date_start, "%Y-%m-%d %H:%M:%S")
            dt_end = dt_start + relativedelta.relativedelta(
                hours=self.template_id.estimate_work_hour,
                minutes=self.template_id.estimate_work_minute,
            )
            self.scheduled_date_end = dt_end.strftime("%Y-%m-%d %H:%M:%S")

    @api.multi
    def unlink(self):
        strWarning = _("You can only delete data on draft state")
        for document in self:
            if document.state != "draft":
                if not self.env.context.get("force_unlink", False):
                    raise UserError(strWarning)
        _super = super(UtilityMeterReadingWorksheet, self)
        _super.unlink()
