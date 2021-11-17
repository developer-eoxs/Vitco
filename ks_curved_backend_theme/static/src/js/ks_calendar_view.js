odoo.define("ks_curved_backend_theme.ksCalendarView", function (require) {
  "use strict";

  var CalendarRenderer = require("web.CalendarRenderer");
  var config = require("web.config");

  CalendarRenderer.include({
    _getFullCalendarOptions: function () {
      var res = this._super.apply(this, arguments);

      if (config.device.isMobile) {
        res.views.dayGridMonth.columnHeaderFormat = "ddd";
      }

      return res;
    },
  });
});
