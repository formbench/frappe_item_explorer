frappe.treeview_settings['Product Category'] = {
  breadcrumb: 'Product Category',
  title: 'Product Categories',
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
  // custom buttons to be displayed beside each node
  customize_toolbar: true,
  toolbar: [
    {
      label: 'Edit',
      condition: function (node) {
        return true;
      },
      click: function (node) {
        frappe.set_route('Form', 'Product Category', node.data.value);
      },
      btnClass: 'hidden-xs',
    },
    {
      label: 'Add Child',
      condition: function (node) {
        return true;
      },
      click: function (node) {
        if (node) {
          // create new doc
          frappe.new_doc('Product Category', {
            parent_product_category: node.data.value,
          });
          // set is group of node to true
          frappe.db.set_value(
            'Product Category',
            node.data.value,
            'is_group',
            1
          );
        }
      },
      btnClass: 'hidden-xs',
    },
  ],
};
