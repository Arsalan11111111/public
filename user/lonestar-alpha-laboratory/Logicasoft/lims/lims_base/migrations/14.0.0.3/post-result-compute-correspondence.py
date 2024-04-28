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
def get_parameter_compute_correspondence(cr):
    query = """SELECT id, compute_parameter_id, method_param_charac_id, correspondence, is_optional 
                    FROM lims_parameter_compute_correspondence;"""
    cr.execute(query)
    return cr.fetchall()


def get_result_ids(cr, method_param_charac_id):
    query = "SELECT id FROM lims_analysis_compute_result WHERE method_param_charac_id=%s"
    cr.execute(query, (method_param_charac_id,))
    return cr.fetchall()


def get_charac_data(cr, method_param_charac_id):
    query = "SELECT use_function, formula FROM lims_method_parameter_characteristic WHERE id=%s;"
    cr.execute(query, (method_param_charac_id,))
    return cr.fetchall()


def create_result_correspondence(cr, result_ids, correspondence):
    query = """
            INSERT INTO lims_result_compute_correspondence (method_param_charac_id, correspondence, is_optional,
            compute_result_id, use_function)
            VALUES (%s, %s, %s, %s, %s);
            """
    query2 = "UPDATE lims_analysis_compute_result SET formula = %s WHERE id = %s;"
    charac_data = get_charac_data(cr, correspondence[1])[0]
    use_function = charac_data[0]
    formula = charac_data[1]
    if use_function or formula:
        for result_id in result_ids:
            cr.execute(query, list(correspondence[2:]) + list(result_id) + [use_function])
            cr.execute(query2, (formula, result_id))


def migrate(cr, version):
    """
    Field correspondence_ids on compute results change from related from lims.parameter.compute.correspondence to new
    model lims.result.compute.correspondence
    Re-create data for every existing compute result (there is no old data because related field wasn't store)
    """
    compute_correspondences = get_parameter_compute_correspondence(cr)
    for correspondence in compute_correspondences:
        if correspondence[1] and correspondence[2]:
            result_ids = get_result_ids(cr, correspondence[1])
            create_result_correspondence(cr, result_ids, correspondence)
