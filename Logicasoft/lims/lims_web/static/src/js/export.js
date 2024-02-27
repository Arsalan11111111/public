/** @odoo-module alias=lims_web.export */

import publicWidget from 'web.public.widget';

publicWidget.registry.ExportAnalysisResults = publicWidget.Widget.extend({
    selector: '.o_export_analysis_results',
    events: {
        'click': '_onClick',
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onClick: function (ev) {
        var $wrap = this.$el.closest('div#wrap');
        var $activeTab = $wrap.find('div.tab-pane.show');
        var sheetName = $wrap.find('ul.nav-tabs').find('a.nav-link.active').text().trim();
        var sampleName = $wrap.find('span.o_sample_name').text().trim();
        var wb = XLSX.utils.table_to_book($activeTab.find('table.table')[0], {sheet: sheetName});
        var wbName = '%s_%n.xlsx'.replace('%s', sampleName).replace('%n', sheetName);
        if ($(ev.currentTarget).data('all')) {
            var $inactiveTabs = $wrap.find('div.tab-pane:not(.show)');
            var $sheets = $wrap.find('ul.nav-tabs').find('a.nav-link:not(.active)');
            var otherSheetNames = [];
            var otherSheets = [];
            _.each($sheets, function (sheet) {
                var name = $(sheet).text().trim();
                wb.SheetNames.push(name);
                otherSheetNames.push(name);
            });
            _.each($inactiveTabs, function (inactiveTab) {
                var $table = $(inactiveTab).find('table.table')[0];
                otherSheets.push(XLSX.utils.table_to_sheet($table));
            });
            _.each(otherSheetNames, function (sn, i) {
                wb.Sheets[sn] = otherSheets[i];
            });
            wbName = '%s_All_Results.xlsx'.replace('%s', sampleName);
        }
        // TODO: issue with number like '10,0000' = '100000', should be '10.0'
        XLSX.writeFile(wb, wbName);
    },
});
