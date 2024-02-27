/** @odoo-module alias=lims_web.lims_web */

import publicWidget from 'web.public.widget';

publicWidget.registry.AnalysisPortalForm = publicWidget.Widget.extend({
    selector: 'div.o_analysis_portal_form',

    /**
     * @override
     */
    start: function () {
        var showSubmitBtn = this.$el.find('select, input').length;
        this.$el.find('button.o_submit_btn_form').toggleClass('d-inline', showSubmitBtn);
    },
});
