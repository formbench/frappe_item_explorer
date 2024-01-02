frappe.listview_settings['Item Explorer'] = {
  onload() {
    frappe.set_route(['item-explorer', 'view', 'tree']);
  },
  refresh() {
    frappe.set_route(['item-explorer', 'view', 'tree']);
  },
};
