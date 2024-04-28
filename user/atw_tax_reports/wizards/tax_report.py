# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


import logging

_logger = logging.getLogger(__name__)


class TaxReport(models.TransientModel):
    _name = "wizard.tax.report"
    _description = "Wizard: Tax Report"

    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )

    start_date = fields.Date(
        string="From",
        required=True,
        default=lambda self: fields.Date.to_string(
            datetime.date.today().replace(day=1)
        ),
    )
    end_date = fields.Date(
        string="To",
        required=True,
        default=lambda self: fields.Date.to_string((
            datetime.datetime.now() + relativedelta(months=+1, day=1, days=-1)
        ).date()),
    )

    def print_report(self):
        context = self._context
        datas = {"ids": context.get("active_ids", [])}
        datas["model"] = "wizard.tax.report"
        datas["form"] = self.read()[0]
        datas["formatted_start_date"] = self.start_date.strftime('%d/%m/%Y')
        datas["formatted_end_date"] = self.end_date.strftime('%d/%m/%Y')
        datas["start_date"] = self.start_date
        datas["end_date"] = self.end_date
        datas["vatin"] = self.company_id.vat
        datas["company"] = self.company_id.name

        for field in datas["form"].keys():
            if isinstance(datas["form"][field], tuple):
                datas["form"][field] = datas["form"][field][0]
        return self.env.ref(
            "atw_tax_reports.tax_report"
        ).report_action(
            self, data=datas
        )
