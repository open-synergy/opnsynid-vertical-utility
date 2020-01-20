# -*- coding: utf-8 -*-
# Copyright 2019-2020 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Utility Management - Accounting Integration",
    "version": "8.0.1.5.1",
    "category": "Invoicing",
    "website": "https://opensynergy-indonesia.com",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "utility_base",
        "account_accountant",
        "base_terminate_reason",
    ],
    "external_dependencies": {
        "python": [
            "pandas",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/base_sequence_configurator_data.xml",
        "data/base_workflow_policy_data.xml",
        "data/base_cancel_reason_configurator_data.xml",
        "data/base_terminate_reason_configurator_data.xml",
        "data/product_pricelist_type_data.xml",
        "menu.xml",
        "views/utility_type_views.xml",
        "views/utility_contract_invoice_item_views.xml",
        "views/utility_contract_views.xml",
        "views/utility_contract_template_views.xml",
        "views/utility_meter_reading_views.xml",
        "views/utility_contract_invoice_schedule_views.xml",

    ],
}
