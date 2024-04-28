odoo.define('form_followup.KanbanRecordFormFollowup', ['web.KanbanRecord'], function (require){
    "use strict";

    var KanbanRecord = require('web.KanbanRecord');

    KanbanRecord.include({
        _render: function () {
            var res = this._super.apply(this, arguments);
            if (this.$('td.color_line').length){
                this.$('td.color_line').css("background-color", this.record['rel_color'].raw_value);
            }
            return res;
        },
    });
});
