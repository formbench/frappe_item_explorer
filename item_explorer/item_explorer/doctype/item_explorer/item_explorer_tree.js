frappe.treeview_settings['Item Explorer'] = {
  breadcrumb: 'Items',
  title: 'Item Explorer',
  filters: [
    {
      fieldname: 'item_code',
      fieldtype: 'Link',
      options: 'Item',
      label: 'Item',
    },
  ],
  get_tree_nodes:
    'item_explorer.item_explorer.doctype.item_explorer.item_explorer.get_children',
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
  // custom buttons to be displayed beside each node
  toolbar: [
    {
      label: 'View',
      condition: function (node) {
        return node.data.type == 'Item' || node.data.type == 'Variant Item';
      },
      click: function (node) {
        window.open('/Item/' + node.data.value);
      },
      btnClass: 'hidden-xs',
    },
    {
      label: 'Edit Category',
      condition: function (node) {
        return node.data.type == 'Category';
      },
      click: function (node) {
        window.open('/app/product-category/' + node.data.value);
      },
      btnClass: 'hidden-xs',
    },
    {
      label: 'Edit Item',
      condition: function (node) {
        return node.data.type == 'Item' || node.data.type == 'Variant Item';
      },
      click: function (node) {
        window.open('/app/item/' + node.data.value);
      },
      btnClass: 'hidden-xs',
    },
  ],
  // enable custom buttons beside each node
  extend_toolbar: false,
};
