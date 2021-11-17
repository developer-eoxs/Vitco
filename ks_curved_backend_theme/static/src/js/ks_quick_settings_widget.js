odoo.define(
  "ks_curved_backend_theme.ks_quick_settings_widget",
  function (require) {
    "use strict";

    var core = require("web.core");
    var qweb = core.qweb;
    var ajax = require("web.ajax");
    var SystrayMenu = require("web.SystrayMenu");
    var Widget = require("web.Widget");
    var SwitchCompanyMenu = require("web.SwitchCompanyMenu");
    var session = require("web.session");
    var web_time = require("web.time");
    var utils = require("web.utils");
    var ajax = require("web.ajax");
    var Dialog = require("web.Dialog");
    var _t = core._t;

    // Change the sequence of Switch company Menu
    SwitchCompanyMenu.include({
      sequence: 2,
    });

    var KsQuickSettings = Widget.extend({
      template: "ks_quick_settings",

      file_type_magic_word: {
        "/": "jpg",
        R: "gif",
        i: "png",
        P: "svg+xml",
      },

      events: {
        "click .btn-global-settings": "_ksGlobalSettings",
        "click .ks_user_settings": "_ksUserSettings",
        "click .ks-dropdown-close": "_ksHideUserSettings",
        "click .ks_body_background_del, .ks_drawer_background_del":
          "_ksDelBackgroundImage",
        "change input": "_onInputChange",
        "click button.ks_setting_save": "_ksSettingSave",
        "click button.ks_setting_cancel": "_ksSettingCancel",
        "click button#ks_add_custom_theme_user": "_ksUserCustomThemeAdd",
        "click .ks_background_default": "_ksBackgroundDefault",
        "click .ks_drawer_background_default": "_ksDrawerBackgroundDefault",
        "click .ks_user_theme_edit": "_ksUserThemeEdit",
        "click .ks_user_theme_delete": "_ksUserThemeDelete",
        "click .ks_theme_edit_cancel": "_ksUserThemeCancel",
        "click .ks_theme_edit_update": "_ksUserThemeUpdate",
        "click .ks_new_theme_save": "_ksUserThemeSave",
      },
      // force this item to be the first one to the left of the UserMenu in the systray
      sequence: 1,
      /**
       * @override
       **/
      init: function () {
        this._super.apply(this, arguments);
        // Prevent it to call quickly again again
        this._onSwitchCompanyClick = _.debounce(
          this._onSwitchCompanyClick,
          1500,
          true
        );
        this.data = false;
        this.ks_unsaved_setting = {};
        this.ks_user_theme_fields = [
          "ks_body_background",
          "ks_menu",
          "ks_menu_hover",
          "ks_button",
          "ks_border",
          "ks_heading",
          "ks_link",
          "ks_primary_color",
          "ks_tooltip",
        ];
      },
      /**
       * @override
       **/
      willStart: async function () {
        const _super = this._super.bind(this);

        const data = await this._rpc({
          route: "/render/theme/view/data",
          params: { ks_setting_scope: "User" },
        });
        this.data = data;

        // Applying color theme
        const ks_current_theme = await this._rpc({
          route: "/ks_curved_backend_theme/getTheme",
          params: {},
        });
        // Add current theme info on color theme.
        session.ks_color_theme = ks_current_theme;

        // Todo: Remove this line if no use.
        // Update configuration values to session for further use.
        session.ks_curved_backend_theme_data = data;

        // Apply css based on the scopes.
        const ks_dynamic_css = await this._rpc({
          model: "ks.global.config",
          method: "ks_get_value_from_scope",
          args: [
            [
              "ks_button_style",
              "ks_theme_style",
              "ks_tab_style",
              "ks_font_style",
              "ks_separator_style",
              "ks_checkbox_style",
              "ks_font_size",
              "ks_chatter",
              "ks_radio_button_style",
              "ks_popup_animation_style",
            ],
          ],
        });

        const ks_drawer_details = await this._rpc({
          model: "ks.global.config",
          method: "get_body_background",
          args: [["ks_app_drawer_background"]],
        });
        if (ks_drawer_details && ks_drawer_details.ks_drawer_font_style) {
          $("html").attr(
            "data-drawer-font-style",
            ks_drawer_details.ks_drawer_font_style
          );
        }

        if (ks_dynamic_css && ks_dynamic_css.ks_button_style) {
          ajax.loadCSS(
            `/ks_curved_backend_theme/static/src/scss/components/buttons/${ks_dynamic_css.ks_button_style}.css`
          );
        }
        if (ks_dynamic_css && ks_dynamic_css.ks_theme_style) {
          ajax.loadCSS(
            `/ks_curved_backend_theme/static/src/scss/components/theme_style/${ks_dynamic_css.ks_theme_style}.css`
          );
        }
        if (ks_dynamic_css && ks_dynamic_css.ks_tab_style) {
          ajax.loadCSS(
            `/ks_curved_backend_theme/static/src/scss/components/tab_style/${ks_dynamic_css.ks_tab_style}.css`
          );
        }

        if (ks_dynamic_css && ks_dynamic_css.ks_font_style) {
          ajax.loadCSS(
            `/ks_curved_backend_theme/static/src/scss/components/fonts/${ks_dynamic_css.ks_font_style}.css`
          );
        }

        if (ks_dynamic_css && ks_dynamic_css.ks_separator_style) {
          ajax.loadCSS(
            `/ks_curved_backend_theme/static/src/scss/components/separators/${ks_dynamic_css.ks_separator_style}.css`
          );
        }

        if (ks_dynamic_css && ks_dynamic_css.ks_checkbox_style) {
          ajax.loadCSS(
            `/ks_curved_backend_theme/static/src/scss/components/checkbox/${ks_dynamic_css.ks_checkbox_style}.css`
          );
        }

        if (ks_dynamic_css && ks_dynamic_css.ks_font_size) {
          ajax.loadCSS(
            `/ks_curved_backend_theme/static/src/scss/components/fontsize/${ks_dynamic_css.ks_font_size}.css`
          );
        }

        if (ks_dynamic_css && ks_dynamic_css.ks_chatter == "ks_chatter_right") {
          ajax.loadCSS(
            `/ks_curved_backend_theme/static/src/scss/components/chatter/${ks_dynamic_css.ks_chatter}.css`
          );
        }

        if (ks_dynamic_css && ks_dynamic_css.ks_radio_button_style) {
          ajax.loadCSS(
            `/ks_curved_backend_theme/static/src/scss/components/radiobutton/${ks_dynamic_css.ks_radio_button_style}.css`
          );
        }

        if (ks_dynamic_css && ks_dynamic_css.ks_popup_animation_style) {
          ajax.loadCSS(
            `/ks_curved_backend_theme/static/src/scss/components/popup_animation/${ks_dynamic_css.ks_popup_animation_style}.css`
          );
        }

        return _super(...arguments);
      },
      /**
       * @override
       **/
      start: function () {
        var res = this._super.apply(this, arguments);
        var self = this;

        // Remove unused css style
        if (
          this.ks_background &&
          this.ks_background.ks_body_background &&
          this.ks_background.ks_body_background.value
        ) {
        }

        var ks_apply_dark_mode = true;

        // Check light and dark theme.
        if (!this.data.ks_dark_mode) ks_apply_dark_mode = false;

        if (
          this.data.ks_auto_dark_mode &&
          this.data.ks_sun_time_info &&
          this.data.ks_dark_mode
        ) {
          // Check theme light/dark mode based on sun time.
          var ks_current_datetime = new Date();
          var ks_sunrise_datetime = new Date(
            "01 Jan 2000 " + this.data.ks_sun_time_info.sunrise
          );
          var ks_sunset_datetime = new Date(
            "01 Jan 2000 " + this.data.ks_sun_time_info.sunset
          );

          if (
            this._ksCompareTime(
              ks_sunrise_datetime,
              ks_sunset_datetime,
              ks_current_datetime
            )
          ) {
            ks_apply_dark_mode = false;
          }

          // Function auto change light/dark mode.
          //          setInterval(function () {
          //            var ks_current_datetime = new Date();
          //            var ks_current_mode = $("html").attr("data-color-mode");
          //            if (
          //              self._ksCompareTime(
          //                ks_sunrise_datetime,
          //                ks_sunset_datetime,
          //                ks_current_datetime
          //              )
          //            ) {
          //              if (ks_current_mode == "ks-dark") {
          //                $("html").attr("data-color-mode", "ks-light");
          //                session.ks_current_color_mode = "ks-light";
          //              }
          //            } else {
          //              if (ks_current_mode == "ks-light") {
          //                $("html").attr("data-color-mode", "ks-dark");
          //                session.ks_current_color_mode = "ks-dark";
          //              }
          //            }
          //          }, 30000);
        }

        // Apply light/dark theme.
        if (ks_apply_dark_mode) $("html").attr("data-color-mode", "ks-dark");
        else $("html").attr("data-color-mode", "ks-light");
        session.ks_current_color_mode = $("html").attr("data-color-mode");
        this._ksManageCurrentColorTheme();
        return res;
      },

      _ksManageCurrentColorTheme() {
        var ks_current_theme = session.ks_color_theme;
        var ks_header_icon_clr = this._ksGetHeaderIconColor(
          ks_current_theme["body-background"]
        );

        // Change header icons color for light and when body color is dark.
        if (
          session.ks_current_color_mode == "ks-light" &&
          ks_header_icon_clr == "white"
        ) {
          session.ks_color_theme.ks_header_icon_clr = ks_header_icon_clr;
          // Change header font icons to white.
          $("ul.o_menu_systray").addClass("ks_color_theme_dark_header");
          $('.o_main_navbar button.phone-menu-btn').addClass("ks_color_theme_dark_header");
          $('.ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar button.phone-menu-btn').addClass("ks_color_theme_dark_header");
        }

        // Control view bg color.
        if (
          session.ks_current_color_mode == "ks-light" &&
          !ks_current_theme.default_theme
        ) {
          document.body.style.setProperty("--ks-main-control-bg", "#FFFFFF");
          if (ks_header_icon_clr == "white") {
            document.body.style.setProperty("--app-drawar", "#FFFFFF");
          }
        }

        if (ks_current_theme.primary) {
          document.body.style.setProperty(
            "--primary",
            ks_current_theme.primary
          );
          if (
            ks_current_theme["body-background"] == ks_current_theme.primary &&
            session.ks_current_color_mode == "ks-light"
          ) {
            document.body.style.setProperty("--nav-primary", "#ffffff");
          } else {
            document.body.style.setProperty(
              "--nav-primary",
              ks_current_theme.primary
            );
          }
        }

        if (ks_current_theme["primary-btn"]) {
          document.body.style.setProperty(
            "--primary-btn",
            ks_current_theme["primary-btn"]
          );
        }

        if (ks_current_theme["tooltip-heading-bg"]) {
          document.body.style.setProperty(
            "--tooltip-heading-bg",
            ks_current_theme["tooltip-heading-bg"]
          );
        }

        if (ks_current_theme["link-color"]) {
          document.body.style.setProperty(
            "--link-color",
            ks_current_theme["link-color"]
          );
        }

        if (ks_current_theme["heading-color"]) {
          document.body.style.setProperty(
            "--heading-color",
            ks_current_theme["heading-color"]
          );
        }

        if (session.ks_current_color_mode == "ks-light") {
          if (ks_current_theme["body-background"]) {
            document.body.style.setProperty(
              "--body-background",
              ks_current_theme["body-background"]
            );
          }

          // Only apply this variable if not background image is active.
          if (!this.data.ks_body_background_image_enable) {
            if (ks_current_theme["nav-link-color"]) {
              document.body.style.setProperty(
                "--nav-link-color",
                ks_current_theme["nav-link-color"]
              );
            }
            if (ks_current_theme["ks-over-link"]) {
              document.body.style.setProperty(
                "--ks-over-link",
                ks_current_theme["ks-over-link"]
              );
            }
          } else if (
            this.data.ks_body_background_image_enable &&
            !this.data.ks_body_background_img.filter((ks_data) => {
              return ks_data.ks_active == true;
            }).length
          ) {
            if (ks_current_theme["nav-link-color"]) {
              document.body.style.setProperty(
                "--nav-link-color",
                ks_current_theme["nav-link-color"]
              );
            }
            if (ks_current_theme["ks-over-link"]) {
              document.body.style.setProperty(
                "--ks-over-link",
                ks_current_theme["ks-over-link"]
              );
            }
          } else {
            $("ul.o_menu_systray").removeClass("ks_color_theme_dark_header");
            $('.o_main_navbar button.phone-menu-btn').removeClass("ks_color_theme_dark_header");
            $('.ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar button.phone-menu-btn').removeClass("ks_color_theme_dark_header");
          }

          if (ks_current_theme["tab-bg"]) {
            document.body.style.setProperty(
              "--tab-bg",
              ks_current_theme["tab-bg"]
            );
          }
        }
      },

      _onInputChange: function (ev) {
        var self = this;
        if (ev.target.name) {
          if (ev.target.type == "checkbox") {
            var _value = ev.target.checked;
            var _field = ev.target.name;
          } else if (ev.target.type == "radio") {
            if (ev.target.attributes["data-value"]) {
              var _value = ev.target.attributes["data-value"].value;
              var _field = ev.target.name;
            }
          }

          this.ks_unsaved_setting[_field] = _value;

          // Handle binary field fields.
          if ($(ev.currentTarget).hasClass("ks_binary_field")) {
            var file_node = ev.target;
            // Handle body background input change.
            if (file_node.getAttribute("data-model")) {
              var ks_img_src = $(file_node.nextElementSibling)
                .find("img")
                .attr("src");
              var ks_value = self._ksDecodeURLToString(ks_img_src);
              if (
                file_node.id.split("#")[1] &&
                parseInt(file_node.id.split("#")[1])
              ) {
                ks_value = parseInt(file_node.id.split("#")[1]);
              }
              this.ks_unsaved_setting[file_node.name] = false;
              this.ks_unsaved_setting[
                file_node.getAttribute("data-field-save")
              ] = ks_value;
            } else {
              var file = file_node.files[0];
              var field_name = ev.target.name;
              //                        var ks_target = ev.currentTarget;
              utils.getDataURLFromFile(file).then(function (data) {
                data = data.split(",")[1];
                // Create url for file
                var url =
                  "data:image/" +
                  (self.file_type_magic_word[data[0]] || "png") +
                  ";base64," +
                  data;
                $("." + field_name + "_preview").prop("src", url);
                self.ks_unsaved_setting[field_name] = data;
                $(ev.currentTarget)
                  .parents(".ks-quick-card")
                  .find(".ks_bck_img")
                  .removeClass("d-none");
              });
            }
          }
          if ($(ev.currentTarget).attr("class").includes("slider")) {
            $(ev.currentTarget)
              .siblings(".ks_opacity_value_max")
              .html(ev.currentTarget.value);
            this.ks_unsaved_setting[ev.currentTarget.name] =
              ev.currentTarget.value;
          }

          // Hide/show auto dark mode
          if (_field == "ks_dark_mode") {
            this._ksManageAutoDarkMode(_value);
          }

          if (
            _field == "ks_auto_dark_mode" &&
            _value &&
            !session.ks_curved_backend_theme_data.ks_sun_time_info
          ) {
            $("input#ks_auto_dark_mode").prop("checked", false);
            this.ks_unsaved_setting.ks_auto_dark_mode = false;
            this.do_warn(
              _t("Error"),
              _t("Please add sunrise and sunset time from user's preferences.")
            );
          }
        }
      },

      _ksDecodeURLToString: function (URL) {
        return URL.split(",")[1];
      },

      _ksUserSettings: function (ev) {
        this.ks_unsaved_setting = {};
        document.body.classList.add("ks_stop_auto_hide");
      },

      _ksHideUserSettings: function (ev) {
        document.body.classList.remove("ks_stop_auto_hide");
        this._ksResetValues();
        this.ks_unsaved_setting = {};
      },

      _ksGlobalSettings: function (ev) {
        var self = this;
        $(".ks-dropdown-close").click();
        if (!self.data["ks_global_config_id"])
          alert("Curved Theme Configuration Files Corrupted.");
        var dict = {
          name: _t("Lead or Opportunity"),
          res_model: "ks.global.config",
          res_id: self.data["ks_global_config_id"],
          views: [[false, "form"]],
          type: "ir.actions.act_window",
          context: {
            form_view_ref:
              "ks_curved_backend_theme.ks_global_configuration_form",
          },
        };
        return self.do_action(dict);
      },

      _ksResetValues: function () {
        for (var index in this.ks_unsaved_setting) {
          if (typeof session.ks_curved_backend_theme_data[index] == "boolean") {
            $("input#" + index).prop(
              "checked",
              session.ks_curved_backend_theme_data[index]
            );
            if (index == "ks_dark_mode") {
              if (session.ks_curved_backend_theme_data[index])
                $("div#ks_auto_dark_mode_div").css("display", "block");
              else $("div#ks_auto_dark_mode_div").css("display", "none");
            }
            delete this.ks_unsaved_setting[index];
          } else if (
            ![
              "ks_app_drawer_background",
              "ks_body_background",
              "ks_body_background_img",
              "ks_app_drawer_background_img",
            ].includes(index)
          ) {
            $("input#" + session.ks_curved_backend_theme_data[index]).prop(
              "checked",
              true
            );
            delete this.ks_unsaved_setting[index];
          }
          // clear input type file for body background and app drawer background.
          else if (
            ["ks_body_background_img", "ks_app_drawer_background_img"].includes(
              index
            )
          ) {
            $(`p.${index}_user`).addClass("d-none");
            delete this.ks_unsaved_setting[index];
          }
        }
        // Hide/Show Auto-dark mode
        if ("ks_dark_mode" in this.ks_unsaved_setting) {
          this._ksManageAutoDarkMode(
            session.ks_curved_backend_theme_data.ks_dark_mode
          );
        }
        // Hide/Show Auto-dark mode
        if ("ks_dark_mode" in this.ks_unsaved_setting) {
          this._ksManageAutoDarkMode(
            session.ks_curved_backend_theme_data.ks_dark_mode
          );
        }
      },

      _ksSettingSave: function () {
        var self = this;
        if (Object.keys(this.ks_unsaved_setting).length) {
          ajax
            .jsonRpc("/save/theme/settings", "call", {
              ks_unsaved_setting: self.ks_unsaved_setting,
              ks_origin_scope: "user",
            })
            .then(function () {
              self.do_action("reload_context");
            });
        }
      },

      _ksSettingCancel: function () {
        this._ksResetValues();
      },

      /*
       * Function to compare two datetime based on times
       * return true if ks_datetime_1 < ks_datetime, otherwise false.
       */
      _ksCompareTime: function (
        ks_sunrise_datetime,
        ks_sunset_datetime,
        ks_current_datetime
      ) {
        var ks_hours = ks_current_datetime.getHours();
        var ks_minutes = ks_current_datetime.getMinutes();
        var ks_seconds = ks_current_datetime.getSeconds();
        var ks_curr_time = new Date(
          "01 Jan 2000 " + ks_hours + ":" + ks_minutes + ":" + ks_seconds
        );
        if (
          ks_sunrise_datetime < ks_curr_time &&
          ks_curr_time < ks_sunset_datetime
        ) {
          return true;
        }
        return false;
      },

      /*
       * Manage auto dark mode.
       */
      _ksManageAutoDarkMode: function (value) {
        if (value) {
          // Show auto dark mode.
          this.$("div#ks_auto_dark_mode_div").css("display", "block");
        } else {
          // Hide.
          this.$("div#ks_auto_dark_mode_div").css("display", "none");
        }
      },

      _ksDelBackgroundImage: function (ev) {
        var self = this;
        var ks_image_id = ev.currentTarget.getAttribute("data-id");
        ks_image_id = ks_image_id.split("#")[1];
        if (ev.target.classList.contains("ks_drawer_background_del")) {
          var ks_model = "ks.drawer.background";
        } else {
          var ks_model = "ks.body.background";
        }
        if (ks_image_id) {
          Dialog.confirm(
            this,
            _t("Are you sure you want to delete this record ?"),
            {
              confirm_callback: function () {
                return this._rpc({
                  model: ks_model,
                  method: "unlink",
                  args: [ks_image_id],
                }).then(function () {
                  self.do_action("reload_context");
                });
              },
            }
          );
        }
      },

      _ksBackgroundDefault: function (ev) {
        var self = this;
        this._rpc({
          route: "/kstheme/background/default",
          params: {
            ks_setting_scope: "User",
            ks_default_info: {
              field: "ks_body_background",
              model: "ks.body.background",
            },
          },
        }).then(function () {
          self.do_action("reload_context");
        });
      },

      _ksDrawerBackgroundDefault: function (ev) {
        var self = this;
        this._rpc({
          route: "/kstheme/background/default",
          params: {
            ks_setting_scope: "User",
            ks_default_info: {
              field: "ks_app_drawer_background",
              model: "ks.drawer.background",
            },
          },
        }).then(function () {
          self.do_action("reload_context");
        });
      },

      _ksUserCustomThemeAdd: function (ev) {
        var self = this;
        var ks_edit_section = qweb.render("ks_theme_edit_section", {
          ks_theme_data: {},
        });
        $("div#user_theme_edit_section").html(ks_edit_section);
        self._scrollToDown();
      },

      _ksUserThemeEdit: function (ev) {
        var self = this;
        var ks_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
        this._rpc({
          model: "ks.color.theme",
          method: "search_read",
          kwargs: {
            domain: [["id", "=", ks_theme_id]],
            fields: [],
          },
        }).then(function (arg) {
          if (arg[0].ks_template_id.length) {
            arg[0].id = false;
          }
          var ks_edit_section = qweb.render("ks_theme_edit_section", {
            ks_theme_data: arg[0],
          });
          $("div#user_theme_edit_section").html(ks_edit_section);
          self._scrollToDown();
        });
      },

      _ksUserThemeCancel: function () {
        // Remove the theme edit section.
        $("div#user_theme_edit_section").html("");
      },

      _ks_get_theme_data_dict: function () {
        var ks_data = {};
        this.ks_user_theme_fields.forEach((ks_element) => {
          ks_data[ks_element] = $(`input#${ks_element}_user`).val();
        });
        return ks_data;
      },

      _ksUserThemeSave: function () {
        var self = this;
        var ks_theme_data = this._ks_get_theme_data_dict();
        ks_theme_data["ks_user"] = session.uid;
        this._rpc({
          model: "ks.color.theme",
          method: "create",
          args: [ks_theme_data],
        }).then(function (create_id) {
          self
            ._rpc({
              model: "ks.color.theme",
              method: "search_read",
              kwargs: {
                domain: [["id", "=", create_id]],
                fields: [],
              },
            })
            .then(function (arg) {
              self.data.ks_color_theme.custom.push(arg[0]);
              var color_theme_temp = qweb.render(
                "ks_color_theme_qweb_template",
                {
                  widget: self,
                }
              );
              $("div.ks_color_theme_qweb_div_user").html(color_theme_temp);
            });
          // location.reload();
        });
      },

      _ksUserThemeUpdate(ev) {
        var self = this;
        var ks_theme_data = this._ks_get_theme_data_dict();
        var ks_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
        this._rpc({
          model: "ks.color.theme",
          method: "write",
          args: [[ks_theme_id], ks_theme_data],
        }).then(function (arg) {
          self
            ._rpc({
              model: "ks.color.theme",
              method: "search_read",
              kwargs: {
                domain: [["id", "=", ks_theme_id]],
                fields: [],
              },
            })
            .then(function (arg) {
              self._updateThemeData(arg[0]);
              // self.data.ks_color_theme.custom.push(arg[0]);
              var color_theme_temp = qweb.render(
                "ks_color_theme_qweb_template",
                {
                  widget: self,
                }
              );
              $("div.ks_color_theme_qweb_div_user").html(color_theme_temp);
            });
          // location.reload();
          //                var ks_edit_section = qweb.render("ks_theme_edit_section", {ks_theme_data: arg[0]});
          //                $('div#user_theme_edit_section').html(ks_edit_section);
        });
      },

      _ksUserThemeDelete: function (ev) {
        var self = this;
        var ks_theme_id = parseInt($(ev.currentTarget).attr("data-theme-id"));
        if (ks_theme_id) {
          Dialog.confirm(
            this,
            _t("Are you sure you want to delete this record ?"),
            {
              confirm_callback: function () {
                return this._rpc({
                  model: "ks.color.theme",
                  method: "unlink",
                  args: [ks_theme_id],
                }).then(function () {
                  self._ksRemoveTheme(ks_theme_id);
                  var color_theme_temp = qweb.render(
                    "ks_color_theme_qweb_template",
                    {
                      widget: self,
                    }
                  );
                  $("div.ks_color_theme_qweb_div_user").html(color_theme_temp);
                  // self.do_action("reload_context");
                });
              },
            }
          );
        }
      },

      _ksRemoveTheme: function (ks_theme_id) {
        var result = false;
        var ks_custom_themes = _.filter(
          this.data.ks_color_theme.custom,
          function (theme) {
            return ks_theme_id != theme.id;
          }
        );
        this.data.ks_color_theme.custom = ks_custom_themes;
        return result;
      },

      _scrollToDown: function () {
        // Scroll down div
        $("div.ks_color_theme_qweb_div_user").scrollTop(
          $("div.ks_color_theme_qweb_div_user")[0].scrollHeight
        );
      },

      _updateThemeData: function (updated_data) {
        var ks_updated_data = _.map(
          this.data.ks_color_theme.custom,
          function (theme) {
            if (theme.id == updated_data.id) return updated_data;
            else return theme;
          }
        );
        this.data.ks_color_theme.custom = ks_updated_data;
      },

      _ksHexToRGB: function (hex) {
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result
          ? {
              r: parseInt(result[1], 16),
              g: parseInt(result[2], 16),
              b: parseInt(result[3], 16),
            }
          : null;
      },

      _ksGetHeaderIconColor: function (ks_color) {
        var rgb = [];
        var ks_up_color = this._ksHexToRGB(ks_color);
        rgb[0] = ks_up_color.r;
        rgb[1] = ks_up_color.g;
        rgb[2] = ks_up_color.b;

        const ks_brightness = Math.round(
          (parseInt(rgb[0]) * 299 +
            parseInt(rgb[1]) * 587 +
            parseInt(rgb[2]) * 114) /
            1000
        );
        const ks_result = ks_brightness > 125 ? "black" : "white";

        return ks_result;
      },
    });
    SystrayMenu.Items.push(KsQuickSettings);
    return KsQuickSettings;
  }
);
