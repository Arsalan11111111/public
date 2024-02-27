odoo.define('lims_scan_advanced.FormView', function (require) {
"use strict";

var BarcodeEvents = require('web.FormController');

BarcodeEvents.include({
    _quantityListener: function (ev) {
        var character = String.fromCharCode(ev.which);
        if (character === '?') {
            document.activeElement.blur();
        } else {
            this._super.apply(this, arguments);
        }
    },
});

});
