odoo.define("ks_curved_backend_theme.ks_bookmarks", function (require) {
  "use strict";

  var Widget = require("web.Widget");
  var ajax = require("web.ajax");
  var core = require("web.core");
  var _t = core._t;

  var qweb = core.qweb;

  var KsBookmarks = Widget.extend({
    template: "ks_curved_backend_theme.bookmark_bar",
    events: _.extend({}, Widget.prototype.events, {
      "click .ks-bookmarks-menu-toggle": "_ksBookmarksToggle",
      "click .ks-save-bookmark": "_ksSaveBookmark",
      "show.bs.dropdown .ks_add_bookmark_dropdown": "_ksAddBookmark",
      "click #addBookmarkDropdown": "_ksAddBookmarkDiv",
      "click .ks-btn-inn": "_ksSizeInc",
      "click .ks-btn-dec": "_ksSizeDec",
      "click .ks-btn-reset": "_ksSizeReset",
      "click .ks-btn-zoom": "_ksZoomButton",
      "contextmenu .bookmark-link": "_ksRightClick",
    }),

    init: function () {
      var self = this;
      document.bookmark_id;
      document.bookmark_name;
      document.bookmark_position;
      this._super.apply(this, arguments);
    },

    start: function () {
      var self = this;
      ajax.jsonRpc("/render/bookmarks", "call", {}).then(function (data) {
        $(".ks-bookmark-panel").append(data);
      });
      $("body").append(
        '<div class="ks-bookmark-dropdown">' +
          '<div class="ks-bookmark-dropdown-content">' +
          '<div id="ks-bookmark-rename" class="ks-bookmark-option">Rename</div>' +
          '<div id="ks-bookmark-delete" class="ks-bookmark-option">Delete</div>' +
          '<div id="ks-bookmark-moveup" class="ks-bookmark-option">Move-Up</div>' +
          '<div id="ks-bookmark-movedown" class="ks-bookmark-option">Move-Down</div>' +
          "</div>" +
          "</div>"
      );

      $("body").append(
        '<div id="renameBookmarkDropdown" class="ks-rename-bookmark-dropdown">' +
          '<div class="ks-rename-bookmark-header pt-2 px-3">Rename</div>' +
          '<div class="ks-rename-bookmark-body py-2 px-3">' +
          '<div class="form-group m-0">' +
          '<input type="text" class="form-control" placeholder="Name" id="ks_rename_bookmark"/>' +
          "</div>" +
          "</div>" +
          '<div class="ks-rename-bookmark-footer py-2 px-3">' +
          '<button type="button" class="btn btn-primary ks-rename-bookmark">Rename</button>' +
          '<button type="button" class="btn btn-default ks-rename-cancel">Cancel</button>' +
          "</div>" +
          "</div>"
      );
      document
        .getElementById("ks-bookmark-rename")
        .addEventListener("click", self._ksBookmarkRename);
      document
        .getElementById("ks-bookmark-delete")
        .addEventListener("click", self._ksBookmarkDelete);
      document
        .getElementById("ks-bookmark-moveup")
        .addEventListener("click", self._ksBookmarkMoveup);
      document
        .getElementById("ks-bookmark-movedown")
        .addEventListener("click", self._ksBookmarkMovedown);
    },

    // Displayed using bootstrap
    _ksAddBookmark: function (ev) {
      $("#bookmark_name").val("");
    },
    // To prevent closing of div
    _ksAddBookmarkDiv: function (ev) {
      if (!ev.target.classList.contains("btn")) {
        ev.stopPropagation();
        ev.preventDefault();
        $("#ks_bookmark_alert").hide("slow");
      }
    },

    _ksSaveBookmark: function (ev) {
      if ($("#bookmark_name").val() == false) {
        ev.stopPropagation();
        ev.preventDefault();
        $("#ks_bookmark_alert").show("slow");
      } else {
        var bookmark_name = $("#bookmark_name").val();
        var bookmark_url =
          "/web#" + location.href.replace(/^[^#]*#?(.*)$/, "$1");
        var bookmark_position = $(".bookmark-item").length + 1;
        $("#addBookmarkDropdown").toggleClass("show");
        ajax
          .jsonRpc("/update/bookmarks", "call", {
            create_new: "create_new",
            bookmark_name: bookmark_name,
            bookmark_url: bookmark_url,
            bookmark_position: bookmark_position,
          })
          .then(function (data) {
            $(".ks-bookmark-panel").html(data);
            $(".ks_add_bookmark_dropdown").dropdown("dispose");
          });
        $("#ks_bookmark_alert").hide("slow");
      }
    },

    _ksBookmarksToggle: function () {
      document.body.classList.toggle("ks_show_bookmark");
    },

    _ksRightClick: function (event) {
      document.bookmark_id = event.currentTarget.getAttribute("data-id");
      document.bookmark_position =
        event.currentTarget.getAttribute("data-position");
      document.bookmark_name = event.currentTarget.getAttribute("data-name");
      $("#ks-bookmark-movedown").removeClass("d-none");
      $("#ks-bookmark-moveup").removeClass("d-none");
      if (document.bookmark_position == $(".bookmark-item").length) {
        $("#ks-bookmark-movedown").addClass("d-none");
      }
      if (document.bookmark_position == "1") {
        $("#ks-bookmark-moveup").addClass("d-none");
      }
      $(".ks-bookmark-dropdown").css({
        left: event.pageX - $(".ks-bookmark-dropdown").width(),
        top: event.pageY,
        display: "block",
      });
      window.addEventListener("click", () => {
        $(".ks-bookmark-dropdown").hide();
      });
      event.preventDefault();
    },

    // --- Zoom Functionality --- //
    ksResize: function (scale_value) {
      document.querySelector(".ks-zoom-per").innerText =
        String(scale_value) + "%";
      var o_content_style = document.querySelector(
        ".o_content div:last-child"
      ).style;
      o_content_style.transform = "scale(" + scale_value / 100 + ")";
      o_content_style.transformOrigin = "left top";
      if ($('body.o_rtl').length)
        o_content_style.transformOrigin = "right top";
      o_content_style.width = 100 * (100 / scale_value) + "%";
      o_content_style.flex = "0 0 " + 100 * (100 / scale_value) + "%";
    },
    // Displayed using bootstrap
    _ksZoomButton: function (ev) {
      window.addEventListener("click", () => {
        $("#zoomPanel").removeClass("show");
      });
    },
    _ksSizeInc: function (ev) {
      ev.stopPropagation();
      if ($(".o_content").length) {
        var scale_value =
          parseInt(
            document.querySelector(".ks-zoom-per").innerText.replace("%", "")
          ) + 10;
        this.ksResize(scale_value);
        $(".ks-btn-dec")[0].removeAttribute("disabled");
        if (scale_value >= 500) {
          ev.currentTarget.setAttribute("disabled", true);
        }
      }
    },
    _ksSizeDec: function (ev) {
      ev.stopPropagation();
      if ($(".o_content").length) {
        var scale_value =
          parseInt(
            document.querySelector(".ks-zoom-per").innerText.replace("%", "")
          ) - 10;
        this.ksResize(scale_value);
        $(".ks-btn-inn")[0].removeAttribute("disabled");
        if (scale_value <= 20) {
          ev.currentTarget.setAttribute("disabled", true);
        }
      }
    },
    _ksSizeReset: function (ev) {
      ev.stopPropagation();
      if ($(".o_content").length) {
        document
          .querySelector(".o_content div:last-child")
          .removeAttribute("style");
        document.querySelector(".ks-zoom-per").innerText = "100%";
      }
    },

    // --- Bookmark --- //
    _ksBookmarkRename: function () {
      $("#ks_rename_bookmark").val(document.bookmark_name);
      $(".ks-rename-bookmark-dropdown").css({
        left: event.pageX - $(".ks-rename-bookmark-dropdown").width(),
        top: event.pageY,
        display: "block",
      });
      $(".ks-rename-cancel")[0].addEventListener("click", () => {
        $(".ks-rename-bookmark-dropdown")[0].style.display = "none";
      });

      $(".ks-rename-bookmark")[0].addEventListener("click", () => {
        var name = $("#ks_rename_bookmark").val();
        var id = document.bookmark_id;
        if (name == false) {
          this.call("notification", "notify", {
            title: _t("Can't be Empty"),
            message: _t("Please enter the Name of Bookmark."),
            sticky: false,
          });
        } else {
          $(".ks-rename-bookmark-dropdown")[0].style.display = "none";
          ajax
            .jsonRpc("/update/bookmarks", "call", {
              bookmark_name: name,
              rename: "rename",
              bookmark_id: id,
            })
            .then(function (data) {
              $(".ks-bookmark-panel").html(data);
            });
        }
      });
      event.preventDefault();
    },
    _ksBookmarkDelete: function () {
      var id = document.bookmark_id;
      ajax
        .jsonRpc("/update/bookmarks", "call", {
          delete: "delete",
          bookmark_id: id,
        })
        .then(function (data) {
          $(".ks-bookmark-panel").html(data);
        });
    },
    _ksBookmarkMoveup: function () {
      var id = document.bookmark_id;
      ajax
        .jsonRpc("/update/bookmarks", "call", {
          reposition: "move_up",
          bookmark_position: document.bookmark_position,
          bookmark_id: document.bookmark_id,
        })
        .then(function (data) {
          $(".ks-bookmark-panel").html(data);
        });
    },
    _ksBookmarkMovedown: function () {
      ajax
        .jsonRpc("/update/bookmarks", "call", {
          reposition: "move_down",
          bookmark_position: document.bookmark_position,
          bookmark_id: document.bookmark_id,
        })
        .then(function (data) {
          $(".ks-bookmark-panel").html(data);
        });
    },
  });
  return KsBookmarks;
});
