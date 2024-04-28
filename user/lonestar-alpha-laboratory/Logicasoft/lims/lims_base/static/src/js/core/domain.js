odoo.define('web.Domain.lims.override', function (require) {

'use strict';

var Domain = require('web.Domain');

Domain.include({
    /**
     * @override
     * @param {Array|string} domain
     * @returns {string}
     */
    arrayToString: function (domain) {
        if (_.isString(domain)) return domain;
        return JSON.stringify(domain || [])
            .replace(/false/g, "False")
            .replace(/true/g, "True");
    },
});

});
