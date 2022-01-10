# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.tools.safe_eval import safe_eval as eval  # pylint: disable=W0622


class UtilityContractTemplate(models.Model):
    _name = "utility.contract_template"
    _description = "Utility Contract Template"

    name = fields.Char(
        string="Template",
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
    contract_sequence_id = fields.Many2one(
        string="Contract Sequence",
        comodel_name="ir.sequence",
        company_dependent=True,
    )
    default_journal_id = fields.Many2one(
        string="Default Sale Journal",
        comodel_name="account.journal",
        company_dependent=True,
        required=True,
    )
    default_receivable_account_id = fields.Many2one(
        string="Default Receivable Account",
        comodel_name="account.account",
        company_dependent=True,
        required=True,
    )
    default_bank_account_id = fields.Many2one(
        string="Default Bank Account",
        comodel_name="res.partner.bank",
        company_dependent=True,
    )
    default_payment_term_id = fields.Many2one(
        string="Default Payment Term",
        comodel_name="account.payment.term",
        company_dependent=True,
    )
    python_code_invoice_description = fields.Text(
        string="Python Code for Invoice Description",
        default="""
result = "Invoice %s for contract %s (%s - %s)" % (
document.contract_id.meter_id.type_id.name,
document.contract_id.name,
document.period_start_date,
document.schedule_date,
)
""",
    )
    contract_confirm_grp_ids = fields.Many2many(
        string="Allow To Confirm Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_confirm_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_approve_grp_ids = fields.Many2many(
        string="Allow To Approve Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_approve_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_start_grp_ids = fields.Many2many(
        string="Allow To Confirm Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_start_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_done_grp_ids = fields.Many2many(
        string="Allow To Finish Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_done_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_cancel_grp_ids = fields.Many2many(
        string="Allow To Cancel Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_cancel_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_terminate_grp_ids = fields.Many2many(
        string="Allow To Terminate Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_terminate_contract",
        column1="template_id",
        column2="group_id",
    )
    contract_restart_grp_ids = fields.Many2many(
        string="Allow To Restart Contract",
        comodel_name="res.groups",
        relation="rel_contract_template_restart_contract",
        column1="template_id",
        column2="group_id",
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
    def _get_invoice_description(self, document):
        self.ensure_one()
        localdict = self._get_localdict(document)
        try:
            eval(
                self.python_code_invoice_description,
                localdict,
                mode="exec",
                nocopy=True,
            )
            result = localdict["result"]
        except:  # noqa: E722
            result = "/"
        return result
