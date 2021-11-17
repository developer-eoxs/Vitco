odoo.define("ks_curved_backend_theme.AbstractWebClient", function (require) {
  "use strict";

  var AbstractWebClient = require("web.AbstractWebClient");

  var KsAbstractWebClient = AbstractWebClient.include({
    init: function (parent) {
      this._super.apply(this, arguments);
      var temp_this = this;
      this._rpc({ route: "/ks_curved_theme/ks_get_website_title" }).then(
        function (result) {
          temp_this.set("title_part", { zopenerp: result });
        }
      );
    },
  });
});
