odoo.define(
  "ks_curved_backend_theme.ks_global_config_widget",
  function (require) {
    "use strict";

    var core = require("web.core");
    var Widget = require("web.Widget");
    var widgetRegistry = require("web.widget_registry");
    var ajax = require("web.ajax");
    var utils = require("web.utils");
    var Dialog = require("web.Dialog");
    var session = require("web.session");
    var QWeb = core.qweb;
    var _t = core._t;

    var QWeb = core.qweb;

    var KsGlobalConfigWidget = Widget.extend({
      template: "ks_global_settings",

      file_type_magic_word: {
        "/": "jpg",
        R: "gif",
        i: "png",
        P: "svg+xml",
      },

      events: _.extend({}, Widget.prototype.events, {
        "click .ks_global_apply_scope": "_ksApplyScope",
        "change input": "_onInputChange",
        "click .ks_save_global_data": "_ksSaveGlobalData",
        "click .ks_body_background_del_global, .ks_drawer_background_global_del":
          "_ksDelBackgroundImage",
        "click .ks_background_default_global": "_ksBackgroundDefault",
        "click .ks_drawer_background_default_global": "_ksDrawerDefault",
        "click button.ks_setting_cancel_global": "_ksSettingCancel",
        "click .ks_global_theme_edit": "_ksColorThemeEdit",
        "click button#ks_add_custom_theme_global": "_ksCustomColorThemeAdd",
        "click .ks_theme_edit_cancel": "_ksColorThemeCancel",
        "click .ks_new_theme_save": "_ksColorThemeSave",
        "click .ks_theme_edit_update": "_ksColorThemeUpdate",
        "click .ks_global_theme_delete": "_ksColorThemeDelete",
      }),
      // Todo: Take reference from Ribbon widget
      init: function (parent, data, options) {
        this.ks_unsaved_data = {};
        this.ks_unsaved_theme_global_data = {};
        this.ks_global_theme_fields = [
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
        this._super.apply(this, arguments);
      },

      /**
       * @override
       **/
      willStart: async function () {
        const _super = this._super.bind(this);
        const data = await this._rpc({
          args: [],
          method: "ks_get_config_values",
          model: "ks.global.config",
        });
        const ks_theme_global_data = await this._rpc({
          route: "/render/theme/view/data",
          params: { ks_setting_scope: "Global" },
        });
        if (data) {
          this.data = data;
        }
        if (ks_theme_global_data) {
          this.ks_color_theme_scope = ks_theme_global_data.ks_color_theme_scope == 'Global' ? true : false;
          this.ks_theme_global_data = ks_theme_global_data;
        }
        return _super(...arguments);
      },

      _render: function () {
        this._super.apply(this, arguments);
        var ks_self = this;
      },

      _ksApplyScope: function () {
        var self = this;
        if (this.ks_unsaved_data) {
          this._rpc({
            args: [this.ks_unsaved_data],
            method: "ks_save_apply_scope",
            model: "ks.global.config",
          }).then(function () {
            self.do_action("reload_context");
          });
        }
      },

      _onInputChange: function (ev) {
        var self = this;
        if (
          ev.currentTarget.name &&
          ev.currentTarget.dataset.value != this.data[ev.currentTarget.name] &&
          ev.currentTarget.hasAttribute("ks_curve_scope_input")
        ) {
          this.ks_unsaved_data[ev.currentTarget.name] =
            ev.currentTarget.dataset.value;
        } else if (ev.currentTarget.name) {
          delete this.ks_unsaved_data[ev.currentTarget.name];
        }

        // Condition to change global setting fields and boolean fields.
        if (
          ev.currentTarget.name.split("scope").length < 2 &&
          !$(ev.currentTarget).hasClass("ks_binary_field")
        ) {
          this.ks_unsaved_theme_global_data[ev.currentTarget.name] = ev
            .currentTarget.dataset.value
            ? ev.currentTarget.dataset.value
            : ev.currentTarget.checked;
        }
        if ($(ev.currentTarget).attr("class").includes("slider")) {
          $(ev.currentTarget)
            .siblings(".ks_opacity_value_max")
            .html(ev.currentTarget.value);
          this.ks_unsaved_theme_global_data[ev.currentTarget.name] =
            ev.currentTarget.value;
        }

        // Manage data for text fields.
        if (
          ev.currentTarget.name &&
          ev.currentTarget.dataset.type == "ks-char"
        ) {
          this.ks_unsaved_theme_global_data[ev.currentTarget.name] =
            ev.currentTarget.value;
        }

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
            this.ks_unsaved_theme_global_data[file_node.name] = false;
            this.ks_unsaved_theme_global_data[
              file_node.getAttribute("data-field-save")
            ] = ks_value;
          } else {
            var file = file_node.files[0];
            var field_name = ev.target.name;
            utils.getDataURLFromFile(file).then(function (data) {
              data = data.split(",")[1];
              // Create url for file
              var url =
                "data:image/" +
                (self.file_type_magic_word[data[0]] || "png") +
                ";base64," +
                data;
              $("." + field_name + "_preview").prop("src", url);
              self.ks_unsaved_theme_global_data[field_name] = data;
              $(ev.currentTarget)
                .parents(".ks-quick-card")
                .find(".ks_bck_img")
                .removeClass("d-none");
            });
          }
        }
      },

      _ksDecodeURLToString: function (URL) {
        return URL.split(",")[1];
      },

      _ksSaveGlobalData: function (ev) {
        var self = this;
        if (Object.keys(this.ks_unsaved_theme_global_data).length) {
          ajax
            .jsonRpc("/save/theme/settings", "call", {
              ks_unsaved_setting: this.ks_unsaved_theme_global_data,
              ks_origin_scope: "global",
            })
            .then(function () {
              self.do_action("reload_context");
            });
        }
      },

      _ksDelBackgroundImage: function (ev) {
        var self = this;
        var ks_image_id = ev.currentTarget.getAttribute("data-id");
        ks_image_id = ks_image_id.split("#")[1];
        if (ev.target.classList.contains("ks_drawer_background_global_del")) {
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
            ks_setting_scope: "Global",
            ks_default_info: {
              field: "ks_body_background",
              model: "ks.body.background",
            },
          },
        }).then(function () {
          self.do_action("reload_context");
        });
      },

      _ksDrawerDefault: function (ev) {
        var self = this;
        this._rpc({
          route: "/kstheme/background/default",
          params: {
            ks_setting_scope: "Global",
            ks_default_info: {
              field: "ks_app_drawer_background",
              model: "ks.drawer.background",
            },
          },
        }).then(function () {
          self.do_action("reload_context");
        });
      },

      _ksSettingCancel: function () {
        this._ksResetValues();
      },

      _ksResetValues: function () {
        var session = this.ks_theme_global_data;
        var ks_splitter = "_global";
        for (var index in this.ks_unsaved_theme_global_data) {
          let ks_index = index.split(ks_splitter)[0];
          // Ignore unsupported fields.
          if (
            ![
              "ks_app_drawer_background_img",
              "ks_app_drawer_background_opacity",
              "ks_body_background_img",
              "ks_body_background_opacity",
              "ks_company_logo",
              "ks_login_background_image",
              "ks_small_company_logo",
              "ks_website_title",
            ].includes(ks_index)
          ) {
            if (typeof session[ks_index] == "boolean") {
              $(`input#${ks_index}${ks_splitter}`).prop(
                "checked",
                session[ks_index]
              );
            } else if (
              !["ks_app_drawer_background", "ks_body_background"].includes(
                ks_index
              )
            ) {
              $(`input#${session[ks_index]}${ks_splitter}`).prop(
                "checked",
                true
              );
            }
          } else if (
            ["ks_body_background_img", "ks_app_drawer_background_img"].includes(
              index
            )
          ) {
            $(`p.${index}_global`).addClass("d-none");
          }
          delete this.ks_unsaved_theme_global_data[index];
        }
        // Reset background image and color for background and app drawer.
        [
          "ks_body_background_global",
          "ks_app_drawer_background_global",
        ].forEach((element) => {
          $(`input[name=${element}]:checked`).prop("checked", false);
          $(`input[name=${element}][checked=checked]`).prop("checked", true);
        });
      },

      _ksColorThemeEdit: function (ev) {
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
          var ks_edit_section = QWeb.render("ks_theme_edit_section_global", {
            ks_theme_data: arg[0],
          });
          $("div#global_theme_edit_section").html(ks_edit_section);
          self._scrollToDown();
        });
      },

      _scrollToDown: function () {
        // Scroll down div
        $("div.ks_color_theme_qweb_div_global").scrollTop(
          $("div.ks_color_theme_qweb_div_global")[0].scrollHeight
        );
      },

      _ksCustomColorThemeAdd: function () {
        var self = this;
        var ks_edit_section = QWeb.render("ks_theme_edit_section_global", {
          ks_theme_data: {},
        });
        $("div#global_theme_edit_section").html(ks_edit_section);
        self._scrollToDown();
      },

      _ksColorThemeCancel: function () {
        $("div#global_theme_edit_section").html("");
      },

      _ksColorThemeSave: function () {
        var self = this;
        var ks_theme_data = this._ks_get_theme_data_dict();
        ks_theme_data["ks_global"] = true;
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
              self.ks_theme_global_data.ks_color_theme.custom.push(arg[0]);
              var color_theme_temp = QWeb.render(
                "ks_color_theme_qweb_template_global",
                {
                  widget: self,
                }
              );
              $("div.ks_color_theme_qweb_div_global").html(color_theme_temp);
            });
        });
      },

      _ks_get_theme_data_dict: function () {
        var ks_data = {};
        this.ks_global_theme_fields.forEach((ks_element) => {
          ks_data[ks_element] = $(`input#${ks_element}_global`).val();
        });
        return ks_data;
      },

      
      _ksColorThemeUpdate: function (ev) {
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
              var color_theme_temp = QWeb.render(
                "ks_color_theme_qweb_template_global",
                {
                  widget: self,
                }
              );
              $("div.ks_color_theme_qweb_div_global").html(color_theme_temp);
            });
        });
      },

      _updateThemeData: function (updated_data) {
        var ks_updated_data = _.map(this.ks_theme_global_data.ks_color_theme.custom, function (theme) {
          if (theme.id == updated_data.id) return updated_data;
          else return theme;
        });
        this.ks_theme_global_data.ks_color_theme.custom = ks_updated_data;
      },

      _ksColorThemeDelete: function (ev) {
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
                  var color_theme_temp = QWeb.render(
                    "ks_color_theme_qweb_template_global",
                    {
                      widget: self,
                    }
                  );
                  $("div.ks_color_theme_qweb_div_global").html(
                    color_theme_temp
                  );
                });
              },
            }
          );
        }
      },

      _ksRemoveTheme: function (ks_theme_id) {
        var result = false;
        var ks_custom_themes = _.filter(
          this.ks_theme_global_data.ks_color_theme.custom,
          function (theme) {
            return ks_theme_id != theme.id;
          }
        );
        this.ks_theme_global_data.ks_color_theme.custom = ks_custom_themes;
        return result;
      },
    });

    widgetRegistry.add("ks_global_config_widget", KsGlobalConfigWidget);

    return KsGlobalConfigWidget;
  }
);
