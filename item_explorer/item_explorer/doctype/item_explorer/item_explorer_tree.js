frappe.treeview_settings['Item Explorer'] = {
  breadcrumb: 'Items',
  title: __('Item Explorer'),
  filters: [
    {
      fieldname: 'product_category',
      fieldtype: 'Link',
      options: 'Product Category',
      label: __('Product Category'),
    },
  ],
  get_tree_nodes:
    'item_explorer.item_explorer.doctype.item_explorer.item_explorer.get_children',
  show_expand_all: false,
  get_label: function (node) {
    if (!node.data.title) return __('Item Explorer');
    if (node.data.type === 'Category') return node.data.title;
    else return node.data.title + ' (' + node.data.type + ')';
  },
  onload: function (treeview) {
    // triggered when tree view is instanciated
  },
  post_render: function (treeview) {
    // triggered when tree is instanciated
    // You can set args manually here, these will be available in the get_tree_nodes function
    // treeview.args['type'] = lastClickedType
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
      label: __('Show List'),
      condition: function (node) {
        return node.data.type == __('Category');
      },
      click: function (node) {
        const categoryValue = JSON.parse(node.data.value).value;
        const isNotSet = JSON.stringify(['is', 'not set']);
        window.open(
          `/app/item/view/list?variant_of=${isNotSet}&custom_product_category=` +
            (categoryValue === 'others' ? isNotSet : categoryValue)
        );
      },
      btnClass: 'hidden-xs',
    },
    {
      label: __('Show List'),
      condition: function (node) {
        return node.data.type == __('Item');
      },
      click: function (node) {
        const parentValue = JSON.parse(node.data.value).value;
        window.open(`/app/item/view/list?variant_of=${parentValue}`);
      },
      btnClass: 'hidden-xs',
    },
    {
      label: __('View'),
      condition: function (node) {
        return (
          node.data.type == __('Item') ||
          node.data.type == __('Variant Item') ||
          node.data.type == __('BOM Item')
        );
      },
      click: function (node) {
        window.open('/Item/' + JSON.parse(node.data.value).value);
      },
      btnClass: 'hidden-xs',
    },
    {
      label: __('Edit Category'),
      condition: function (node) {
        return (
          node.data.type == __('Category') &&
          JSON.parse(node.data.value).value != 'others'
        );
      },
      click: function (node) {
        window.open(
          '/app/product-category/' + JSON.parse(node.data.value).value
        );
      },
      btnClass: 'hidden-xs',
    },
    {
      label: __('Edit Item'),
      condition: function (node) {
        return (
          node.data.type == __('Item') ||
          node.data.type == __('Variant Item') ||
          node.data.type == __('BOM Item')
        );
      },
      click: function (node) {
        window.open('/app/item/' + JSON.parse(node.data.value).value);
      },
      btnClass: 'hidden-xs',
    },
    {
      label: __('Edit BOM'),
      condition: function (node) {
        return node.data.type == __('BOM');
      },
      click: function (node) {
        window.open('/app/bom/' + JSON.parse(node.data.value).value);
      },
      btnClass: 'hidden-xs',
    },
  ],
  // enable custom buttons beside each node
  extend_toolbar: false,
};
