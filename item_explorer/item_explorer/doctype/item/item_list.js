frappe.listview_settings.Item = {
  onload: function (listview) {
    listview.page.add_inner_button('Item Explorer', function () {
      frappe.set_route(['item-explorer', 'view', 'tree']);
    });
  },
};
