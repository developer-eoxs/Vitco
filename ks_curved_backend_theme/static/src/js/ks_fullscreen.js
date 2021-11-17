odoo.define("ks_curved_backend_theme.ks_fullscreen", function (require) {
  "use strict";

  const ControlPanel = require("web.ControlPanel");
  var core = require("web.core");
  var _t = core._t;
  const config = require("web.config");

  ControlPanel.patch(
    "ks_curved_backend_theme.ks_fullscreen",
    (T) =>
      class extends T {
        // FixMe: Remove if not in use before release
        constructor() {
          super(...arguments);
        }

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
        /*
         * To add FontAwesome class conditionally
         */
        _ksScreenStatus() {
          var ks_status = "Compressed";
          if (window.innerHeight == screen.height) ks_status = "Expanded";
          return ks_status;
        }

        _ksCheckMobileView() {
          if (screen.width > 1024) return false;
          return true;
        }

        _ksCheckSearchPanel() {
          var ks_search_data = this.model.get("sections");
          if (ks_search_data) return true;
          return false;
        }

        _ksSearchFragmentOpen() {
          $(".ks-phone-filter-modal").addClass("show");
        }

        _ksSearchFragmentClose() {
          $(".ks-phone-filter-modal").removeClass("show");
        }


        _ksViewSwitcher(ev) {
          $(".o_cp_switch_buttons").removeClass("show");
          this.trigger("switch-view", {
            view_type: $(ev.currentTarget).attr("ksView"),
          });
        }
      }
  );
  return ControlPanel;
});
