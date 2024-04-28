# -*- coding: utf-8 -*-

##############################################################################
#
#    Odoo Proprietary License v1.0
#
#    Copyright (c) 2013 LogicaSoft SPRL (<http://www.logicasoft.eu>).
#
#    This software and associated files (the "Software") may only be used (executed,
#    modified, executed after modifications) if you have purchased a valid license
#    from the authors, typically via Odoo Apps, or if you have received a written
#    agreement from the authors of the Software.
#
#    You may develop Odoo modules that use the Software as a library (typically
#    by depending on it, importing it and using its resources), but without copying
#    any source code or material from the Software. You may distribute those
#    modules under the license of your choice, provided that this license is
#    compatible with the terms of the Odoo Proprietary License (For example:
#    LGPL, MIT, or proprietary licenses similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
##############################################################################
from odoo import models, fields


def get_checkbox(value):
    if value:
        return "☑"
    else:
        return "☐"


def xls_false(value):
    if not value:
        return ""
    else:
        return value


class SpwTaxAnalysisXlsx(models.AbstractModel):
    _name = 'report.lims_spw_tax_report_xls.report_tax_analysis_xlsx'
    _description = 'Report Lims_spw_analysis_report_xls Report_tax_xlsx model'
    _inherit = 'report.report_xlsx.abstract'

    nb_row = fields.Integer(default=1)

    def generate_xlsx_report(self, workbook, data, analysis_ids):
        for analysis in analysis_ids:
            sheet_analysis = workbook.add_worksheet(analysis.name)
            cell_format_main_title = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'underline': True,
                'align': 'center',
            })
            cell_format_title = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'underline': True,
            })
            cell_format_small_text = workbook.add_format({
                'font_size': 8,
            })
            cell_date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
            cell_format_time = workbook.add_format({'num_format': 'HH:MM'})
            sheet_analysis.set_row(0, 20)

            sheet_analysis.merge_range('A1:I1', "Rapport d'analyse des rejets industriels", cell_format_main_title)
            sheet_analysis.write(1, 0, "Type d'analyse", cell_format_title)
            sheet_analysis.write(2, 0, get_checkbox(analysis.is_supervision), workbook.add_format({'align': 'right'}))
            sheet_analysis.write(2, 11, analysis.is_supervision)
            sheet_analysis.write(2, 1, "Surveillance", cell_format_small_text)
            sheet_analysis.write(2, 3, "S'il s'agit d'une surveillance, c'est la campagne:")
            sheet_analysis.write(3, 2, xls_false(analysis.sampling_point_id.cpt_tax_ids.counted),
                                 workbook.add_format({'align': 'right'}))
            sheet_analysis.write(3, 3, "/", workbook.add_format({'align': 'center'}))
            sheet_analysis.write(3, 4, xls_false(analysis.sampling_point_id.cpt_tax_ids.planned),
                                 workbook.add_format({'align': 'left'}))
            sheet_analysis.write(3, 0, get_checkbox(analysis.is_statement), workbook.add_format({'align': 'right'}))
            sheet_analysis.write(5, 11, analysis.is_statement)
            sheet_analysis.write(3, 1, "Relevé", cell_format_small_text)
            sheet_analysis.write(4, 1, "Surveillance : les mesures réalisées par un laboratoire agréé pour le compte d’un "
                                       "établissement.", cell_format_small_text)
            sheet_analysis.write(5, 1, "Relevé : les mesures réalisées par un laboratoire agréé pour le compte de "
                                       "l’administration ou de la SPGE.", cell_format_small_text)
            sheet_analysis.write(6, 2, "S'il s'agit d'un relevé, de quel type?")
            sheet_analysis.write(7, 0, get_checkbox(analysis.is_statement_A1), workbook.add_format({'align': 'right'}))
            sheet_analysis.write(6, 11, analysis.is_statement_A1)
            sheet_analysis.write(7, 1, "A1")
            sheet_analysis.write(7, 2, get_checkbox(analysis.is_statement_A2), workbook.add_format({'align': 'right'}))
            sheet_analysis.write(7, 11, analysis.is_statement_A2)
            sheet_analysis.write(7, 3, "A2")
            sheet_analysis.write(7, 4, get_checkbox(analysis.is_statement_B), workbook.add_format({'align': 'right'}))
            sheet_analysis.write(8, 11, analysis.is_statement_B)
            sheet_analysis.write(7, 5, "B")
            sheet_analysis.write(7, 6,
                                 "(cf. spécifications du Marché de services pour la réalisation de campagnes\n d’analyses "
                                 "(relevés) dans le cadre des contrats industriels)",
                                 cell_format_small_text)

            sheet_analysis.write(9, 0, "Identification du rejet", cell_format_title)
            sheet_analysis.write(11, 2, "Rejet N°:", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(11, 3, xls_false(analysis.sampling_point_id.sampling_spill_number))
            sheet_analysis.write(11, 4, "Dev N°:", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(11, 5, xls_false(analysis.sampling_point_id.name))
            sheet_analysis.write(11, 6, "(selon le Permis)")
            sheet_analysis.write(12, 2, "Nom de l'entreprise:", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(12, 3, xls_false(analysis.sampling_point_id.partner_id.name))
            sheet_analysis.write(14, 2, "N° de Répértoire taxe:", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(14, 3, xls_false(analysis.sampling_point_id.partner_id.vat))
            sheet_analysis.write(14, 4,
                                 "format: (code INS[5 chiffre]/code secteur[2 chiffres]code incrémental[3 chiffres])",
                                 cell_format_small_text)
            sheet_analysis.write(15, 2, "Site d'exploitation:", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(15, 3, "Rue :", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(15, 4, xls_false(analysis.sampling_point_id.partner_id.street))
            sheet_analysis.write(15, 5, "N° :", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(15, 6, xls_false(analysis.sampling_point_id.partner_id.street_number))
            sheet_analysis.write(16, 3, "Code postal :", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(16, 4, xls_false(analysis.sampling_point_id.partner_id.zip))
            sheet_analysis.write(16, 5, "Commune:", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(16, 6, xls_false(analysis.sampling_point_id.partner_id.city))
            sheet_analysis.write(17, 2, "Type d'eau:", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(17, 3, xls_false(analysis.sampling_point_id.discharge_water_type_id.name))
            sheet_analysis.write(20, 11, analysis.sampling_point_id.discharge_water_type_id.name)

            sheet_analysis.write(19, 0, "Identification du milieu récepteur", cell_format_title)
            sheet_analysis.write(21, 0, "EG1 :", cell_format_small_text)
            sheet_analysis.write(22, 0, "EG2 :", cell_format_small_text)
            sheet_analysis.write(23, 0, "ES :", cell_format_small_text)
            sheet_analysis.write(24, 0, "SS :", cell_format_small_text)

            sheet_analysis.write(26, 0, "Identification du laboratoire agréé", cell_format_title)
            sheet_analysis.write(28, 1, "Nom :", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(28, 2, xls_false(analysis.laboratory_id.company_id.name))
            sheet_analysis.write(29, 2, "Rue :", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(29, 3, xls_false(analysis.laboratory_id.company_id.street))
            sheet_analysis.write(29, 4, "N° :", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(30, 2, "Code postal :", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(30, 3, xls_false(analysis.laboratory_id.company_id.zip))
            sheet_analysis.write(30, 4, "Commune:", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(30, 5, xls_false(analysis.laboratory_id.company_id.city))
            sheet_analysis.write(31, 1, "Contact", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(31, 2, xls_false(analysis.laboratory_id.responsible_id.name))

            sheet_analysis.write(33, 0, "Echantillonnage", cell_format_title)
            sheet_analysis.write(35, 2, "Type de prélèvement :", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(35, 3, get_checkbox(analysis.is_composite_flow), workbook.add_format({'align': 'right'}))
            sheet_analysis.write(34, 11, analysis.is_composite_flow)
            sheet_analysis.write(35, 4, "Proportionnel au débit", cell_format_small_text)
            sheet_analysis.write(35, 6, "Matériel utilisé:", workbook.add_format({'align': 'right'}))
            sheet_analysis.write(35, 7, get_checkbox(analysis.is_sample_equipment_labo),
                                 workbook.add_format({'align': 'right'}))
            sheet_analysis.write(37, 11, analysis.is_sample_equipment_labo)
            sheet_analysis.write(35, 8, "Labo", cell_format_small_text)
            sheet_analysis.write(36, 3, get_checkbox(analysis.is_time_composite), workbook.add_format({'align': 'right'}))
            sheet_analysis.write(35, 11, analysis.is_time_composite)
            sheet_analysis.write(36, 4, "Proportionnel au temps", cell_format_small_text)
            sheet_analysis.write(36, 7, get_checkbox(analysis.is_sample_equipment_site),
                                 workbook.add_format({'align': 'right'}))
            sheet_analysis.write(38, 11, analysis.is_sample_equipment_site)
            sheet_analysis.write(36, 8, "Site après vérification", cell_format_small_text)
            sheet_analysis.write(37, 3, get_checkbox(analysis.is_punctual), workbook.add_format({'align': 'right'}))
            sheet_analysis.write(36, 11, analysis.is_punctual)
            sheet_analysis.write(37, 4, "Ponctuel", cell_format_small_text)
            sheet_analysis.write(38, 2, "Date effective de début :")
            sheet_analysis.write(38, 3, analysis.date_sample_begin, cell_date_format)
            sheet_analysis.write(38, 4, "(jj/mm/aaaa)")
            sheet_analysis.write(38, 5, analysis.date_sample_begin, cell_format_time)
            sheet_analysis.write(38, 6, "(hh:mm)")
            sheet_analysis.write(39, 2, "Date effective de fin :")
            sheet_analysis.write(39, 3, analysis.date_sample, cell_date_format)
            sheet_analysis.write(39, 4, "(jj/mm/aaaa)")
            sheet_analysis.write(39, 5, analysis.date_sample, cell_format_time)
            sheet_analysis.write(39, 6, "(hh:mm)")
            sheet_analysis.write(41, 2, "Durée:")
            sheet_analysis.write(41, 3, "=(D40-D39)*24")
            sheet_analysis.write(41, 4, "(Heure)")
            sheet_analysis.write(42, 1, get_checkbox(analysis.is_under_seal))
            sheet_analysis.write(43, 11, analysis.is_under_seal)
            sheet_analysis.write(42, 2, "Mise sous scellé de l' échantillonneur par le laboratoire agréé",
                                 cell_format_small_text)
            sheet_analysis.write(43, 0, "Mesure du débit", cell_format_title)
            sheet_analysis.write(45, 0, get_checkbox(analysis.is_continuous_debit))
            sheet_analysis.write(44, 11, analysis.is_continuous_debit)
            sheet_analysis.write(45, 1, "En continu")
            sheet_analysis.write(45, 6, "Matériel utilisé:")
            sheet_analysis.write(45, 7, get_checkbox(analysis.is_sample_equipment_labo))
            sheet_analysis.write(47, 11, analysis.is_sample_equipment_labo)
            sheet_analysis.write(45, 8, "Labo")
            sheet_analysis.write(46, 3, "Volume journalier moyen :")
            sheet_analysis.write(46, 4, xls_false(analysis.continuous_debit_measure))
            sheet_analysis.write(46, 5, "m³/j")
            sheet_analysis.write(46, 7, get_checkbox(analysis.is_equipment_site))
            sheet_analysis.write(48, 11, analysis.is_equipment_site)
            sheet_analysis.write(46, 8, "Site après vérification")
            sheet_analysis.write(47, 0, get_checkbox(analysis.is_statement_spill_counter))
            sheet_analysis.write(45, 11, analysis.is_statement_spill_counter)
            sheet_analysis.write(47, 1, "Relevé du compteur rejet")
            sheet_analysis.write(49, 1, "Début")
            sheet_analysis.write(49, 2, xls_false(analysis.statement_date_start), cell_date_format)
            sheet_analysis.write(49, 3, "(jj/mm/aaaa)")
            sheet_analysis.write(49, 4, xls_false(analysis.statement_date_start), cell_format_time)
            sheet_analysis.write(49, 5, "(hh:mm)")
            sheet_analysis.write(49, 6, xls_false(analysis.statement_index_start))
            sheet_analysis.write(49, 7, "m³")
            sheet_analysis.write(50, 1, "Fin")
            sheet_analysis.write(50, 2, xls_false(analysis.statement_date_end), cell_date_format)
            sheet_analysis.write(50, 3, "(jj/mm/aaaa)")
            sheet_analysis.write(50, 4, xls_false(analysis.statement_date_end), cell_format_time)
            sheet_analysis.write(50, 5, "(hh:mm)")
            sheet_analysis.write(50, 6, xls_false(analysis.statement_index_end))
            sheet_analysis.write(50, 7, "m³")
            sheet_analysis.write(51, 5, "Volume journalier moyen :")
            sheet_analysis.write(51, 6, "=(G51-G50)/(C51-C50)")
            sheet_analysis.write(51, 7, "m³/j")
            sheet_analysis.write(53, 0, get_checkbox(analysis.is_debit_other_estimate))
            sheet_analysis.write(46, 11, analysis.is_debit_other_estimate)
            sheet_analysis.write(53, 1, "Autre estimation")
            sheet_analysis.write(53, 3, xls_false(analysis.other_debit_measure))
            sheet_analysis.write(53, 4, "m³/j")
            sheet_analysis.write(54, 2, "Spécifier la méthodologie :")
            sheet_analysis.write(54, 3, xls_false(analysis.other_methodology_description.name))
            sheet_analysis.write(56, 1, get_checkbox(analysis.is_under_seal_debit))
            sheet_analysis.write(49, 11, analysis.is_under_seal_debit)
            sheet_analysis.write(56, 2, "Mise sous scellé du débimètre - enregistreur par le laboratoire agréé")

            sheet_analysis.write(57, 0, "Activité de production (durant la campagne de prélèvement)", cell_format_title)
            sheet_analysis.write(58, 0,
                                 "Cette section n'est à compléter que si le redevable a été autorisé et souhaite rendre "
                                 "une déclaration en formule simplifiée")
            sheet_analysis.write(59, 2, "Secteur d'activité:")
            sheet_analysis.write(59, 3, "code TD_ACTI :")
            sheet_analysis.write(59, 4, "……………")
            sheet_analysis.write(60, 1, "Matière traitée :")
            sheet_analysis.write(60, 6, "Unité")
            for row in range(61, 61 + 8):
                if row not in (64, 65):
                    sheet_analysis.write(row, 0, "●")
                    sheet_analysis.write(row, 4, "Quantitée")
                    sheet_analysis.write(row, 5, "……………")
                    sheet_analysis.write(row, 7, "déclinaison*")
                    sheet_analysis.write(row, 8, "……………")
            sheet_analysis.write(64, 1, "Matière produite :")
            sheet_analysis.write(70, 1, "Pour les codes où l'unité est \"100 jours de travail\" :")
            sheet_analysis.write(71, 1, "Nombre de travailleurs :")
            sheet_analysis.write(71, 4, "……………")
            sheet_analysis.write(71, 3, "ETP")
            sheet_analysis.write(71, 4, "déclinaison*")
            sheet_analysis.write(71, 5, "……………")
            sheet_analysis.write(72, 0, "remarque : estimation pour la période de prélèvement. Un travailleur = 8h/j")
            sheet_analysis.write(72, 4,
                                 "*c'est-à-dire la déclinaison du code TD_ACTI permettant de déterminer le jeu de "
                                 "facteurs de conversion pour un code TD_ACTI donné. Référence: notice explicative pour "
                                 "la déclaration sur les eaux usées industrielles")

            sheet_analysis.write(74, 0, "Résultats d'analyses", cell_format_title)
            sheet_analysis.write(76, 2, "Date d'analyse :")
            sheet_analysis.write(76, 3, xls_false(analysis.date_start), cell_date_format)
            sheet_analysis.write(76, 4, "(jj/mm/aaaa)")
            sheet_analysis.write(76, 5, xls_false(analysis.date_start), cell_format_time)
            sheet_analysis.write(76, 6, "(hh:mm)")
            sheet_analysis.write(78, 1, "Paramètre")
            sheet_analysis.write(78, 3, "Méthode d'analyse")
            # Récupération des résultats à faire
            row = 79
            for resultat in analysis.result_num_ids:
                if resultat.state in ['conform']:
                    sheet_analysis.write(row, 1, resultat.method_param_charac_id.parameter_id.name)
                    sheet_analysis.write(row, 2, resultat.corrected_value)
                    sheet_analysis.merge_range(row, 3, row, 5, resultat.method_param_charac_id.method_id.name)
                    row += 1
            for resultat in analysis.result_compute_ids:
                if resultat.state in ['conform']:
                    sheet_analysis.write(row, 1, resultat.method_param_charac_id.parameter_id.name)
                    sheet_analysis.write(row, 2, resultat.value)
                    sheet_analysis.merge_range(row, 3, row, 5, resultat.method_param_charac_id.method_id.name)
                    row += 1
            for resultat in analysis.result_sel_ids:
                if resultat.state in ['conform']:
                    sheet_analysis.write(row, 1, resultat.method_param_charac_id.parameter_id.name)
                    sheet_analysis.write(row, 2, resultat.value_id.name)
                    sheet_analysis.merge_range(row, 3, row, 5, resultat.method_param_charac_id.method_id.name)
                    row += 1
            for resultat in analysis.result_text_ids:
                if resultat.state in ['conform']:
                    sheet_analysis.write(row, 1, resultat.method_param_charac_id.parameter_id.name)
                    sheet_analysis.write(row, 2, resultat.value)
                    sheet_analysis.merge_range(row, 3, row, 5, resultat.method_param_charac_id.method_id.name)
                    row += 1
            sheet_analysis.write(row, 1, "Réf. Labo de l'échantillon:")
            sheet_analysis.write(row, 2, xls_false(analysis.name))

            sheet_analysis.write(102, 1,
                                 "*TU = 100/EC50-24h. Si EC50-24h est > 100%, l'effluent est considéré comme  non toxique "
                                 "et TU=0 (D.262)")
            sheet_analysis.write(103, 0, "Le rapportage des données ne tient pas compte des seuils de taxation.")
            sheet_analysis.write(104, 0,
                                 "Lorsqu'une valeur est inférieure au seuil de détection de la méthode de mesure, "
                                 "on note \"<LQ\".")

            sheet_analysis.write(105, 0, "Remarques particulières", cell_format_title)
            sheet_analysis.write(106, 0, get_checkbox(analysis.is_note1))
            sheet_analysis.write(106, 1, "Le redevable a entravé la collecte des informations")
            sheet_analysis.write(106, 11, analysis.is_note1)
            sheet_analysis.write(107, 0, get_checkbox(analysis.is_note2))
            sheet_analysis.write(107, 1, "Remarques liées aux difficultés ou particularités du prélévement")
            sheet_analysis.write(107, 11, analysis.is_note2)
            sheet_analysis.write(108, 0, get_checkbox(analysis.is_note3))
            sheet_analysis.write(108, 1, "Remarques liées aux difficultés ou particularité de l'évaluation du débit")
            sheet_analysis.write(108, 11, analysis.is_note3)
            sheet_analysis.write(109, 0, get_checkbox(analysis.is_note4))
            sheet_analysis.write(109, 0, get_checkbox(analysis.is_note4))
            sheet_analysis.write(109, 11, analysis.is_note4)
            sheet_analysis.write(109, 1, "Autre")
            sheet_analysis.write(110, 0, xls_false(analysis.note_txt))
