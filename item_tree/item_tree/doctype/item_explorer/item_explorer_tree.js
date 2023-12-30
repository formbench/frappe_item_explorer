frappe.treeview_settings['Item Explorer'] = {
  breadcrumb: 'Items',
  title: 'Item Explorer',
  filters: [
    {
      fieldname: 'item_code',
      fieldtype: 'Link',
      options: 'Item',
      label: 'Item',
      //   on_change: handle_company_change(),
    },
  ],
  get_tree_nodes:
    'item_tree.item_tree.doctype.item_explorer.item_explorer.get_children',
  //   add_tree_node: 'path.to.whitelisted_method.handle_add_account',
  //   root_label: 'All Tasks',
  // fields for a new node
  //   fields: [
  //     {
  //       fieldtype: 'Data',
  //       fieldname: 'item_name',
  //       label: 'Name',
  //       reqd: true,
  //     },
  //   ],
  // ignore fields even if mandatory
  // ignore_fields: ['parent_account'],
  // to add custom buttons under 3-dot menu group
  //   menu_items: [
  //   {
  //       label: 'New Company',
  //       action: function() { frappe.new_doc('Company', true) },
  //       condition: 'frappe.boot.user.can_create.indexOf('Company') !== -1'
  //   }
  //   ],
  onload: function (treeview) {
    // triggered when tree view is instanciated
  },
  post_render: function (treeview) {
    // triggered when tree is instanciated
  },
  onrender: function (node) {
    // triggered when a node is instanciated
  },
  on_get_node: function (nodes) {
    // triggered when `get_tree_nodes` returns nodes
  },
  // enable custom buttons beside each node
  extend_toolbar: true,
  // custom buttons to be displayed beside each node
  toolbar: [
    {
      label: 'Add Child',
      condition: function (node) {},
      click: function () {},
      btnClass: 'hidden-xs',
    },
  ],
};
