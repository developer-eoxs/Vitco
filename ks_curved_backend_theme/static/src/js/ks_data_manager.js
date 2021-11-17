odoo.define("ks_curved_backend_theme.DataManager", function (require) {
  "use strict";

  var DataManager = require("web.DataManager");
  var session = require("web.session");
  DataManager.include({
    load_views: async function ({ model, context, views_descr }, options = {}) {
      // Hide/close app drawer when new view is loaded.
      let ks_url_hash = window.location.hash;
      if (
        document.body.classList.contains("ks_appsmenu_active") &&
        (ks_url_hash.includes("action") || ks_url_hash.includes("model"))
      ) {
        setTimeout(function () {
          document.body.classList.toggle("ks_appsmenu_active");
          document.body.classList.remove("brightness");

          if (session.ks_current_color_mode == "ks-light") {
            // Apply Color theme back.
            document.body.style.setProperty(
              "--body-background",
              session.ks_color_theme["body-background"]
            );

            document.body.style.setProperty(
              "--nav-link-color",
              session.ks_color_theme["nav-link-color"]
            );

            document.body.style.setProperty(
              "--ks-over-link",
              session.ks_color_theme["ks-over-link"]
            );
          }
          if (session.ks_color_theme.ks_header_icon_clr) {
            $("ul.o_menu_systray").addClass("ks_color_theme_dark_header");
            $('.o_main_navbar button.phone-menu-btn').addClass("ks_color_theme_dark_header");
            $('.ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar button.phone-menu-btn').addClass("ks_color_theme_dark_header");
          }
        }, 1000);
        $("html").attr("data-color-mode", session.ks_current_color_mode);
      }
      return this._super({ model, context, views_descr }, options);
    },
  });

  return DataManager;
});
