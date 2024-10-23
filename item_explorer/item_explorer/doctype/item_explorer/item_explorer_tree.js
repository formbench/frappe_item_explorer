frappe.treeview_settings['Item Explorer'] = {
  breadcrumb: 'Items',
  title: __('Item Explorer'),
  filters: [
    {
      fieldname: 'product_category',
      fieldtype: 'Link',
      options: 'Product Category',
      label: __('Product Category'),
      disable_onchange: true,
    },
    {
      fieldname: 'item_code',
      fieldtype: 'Link',
      options: 'Item',
      label: __('SKU'),
      disable_onchange: true,
    },
    {
      fieldname: 'product_name',
      fieldtype: 'Data',
      label: __('Product Name'),
      disable_onchange: true,
    },
  ],
  get_tree_nodes:
    'item_explorer.item_explorer.doctype.item_explorer.item_explorer.get_children',
  show_expand_all: false,
  get_tree_root: false,
  get_label: function (node) {
    if (node.data.title === "") return __('Not title found');
    if (!node.data.title) return __('Item Explorer');
    if (node.data.type === 'Category' || node.data.type === 'Bundles Folder')
      return node.data.title;
    else
      return (
        '<div class="d-flex flex-row align-items-center">' +
        '<div class="mr-3">' +
        '<img src="' +
        (node.data.image_url || "/assets/item_explorer/item_placeholder.jpg") +
        '" width="50" />' +
        '</div>' +
        '<div style="line-height: 1.8">' +
        node.data.title + '<br />' +
        '<b>' + node.data.name + '</b>' +
        '<span class="badge bg-light ml-1" style="font-size: 12px; background-color: #f4f4f4; border-radius: 4px; padding: 4px; font-weight:normal">' + node.data.type + '</span>' +
        '</div>' +
        '</div>'
      );
  },
  get_icon: function (node) {
    return ""
  },
  onload: function (treeview) {
    frappe.treeview_settings['Item Explorer'].treeview = {};
    $.extend(frappe.treeview_settings['Item Explorer'].treeview, treeview);

    // triggered when tree view is instanciated
    treeview.page.add_inner_button(__('Item List'), function () {
      frappe.set_route('item');
    });

    var changeTriggered = false

    frappe.after_ajax(() => {
      frappe.treeview_settings['Item Explorer'].filters.forEach((filter) => {
        if (filter.default) {
          $("[data-fieldname='" + filter.fieldname + "']").trigger("change");
          changeTriggered = true
        }

        filter.change = function () {
          // override standard onchange behaviour since we want to have more control
          // over when the tree is refreshed
          var val = this.get_value();

          // returning early when the value has not changed will avoid the double refresh of the tree
          if (val === treeview.args[filter.fieldname]) return;

          console.log("val", val);
          treeview.args[filter.fieldname] = val;
          if (val) {
            treeview.root_label = val;
          } else {
            treeview.root_label = treeview.opts.root_label;
          }
          treeview.set_title();
          treeview.make_tree();
          pushFiltersToUrl(treeview);
        };
      });
    });
    if (!changeTriggered) {
      treeview.make_tree();
    }
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
        return node.data.type == __('Parent Item');
      },
      click: function (node) {
        const parentValue = JSON.parse(node.data.value).value;
        window.open(`/app/item/view/list?variant_of=${parentValue}`);
      },
      btnClass: 'hidden-xs',
    },
    {
      label: __('Open Category'),
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
      label: __('Open Item'),
      condition: function (node) {
        return (
          node.data.type == __('Parent Item') ||
          node.data.type == __('Item') ||
          node.data.type == __('Item Variant') ||
          node.data.type == __('Item Variant / Product Bundle') ||
          node.data.type == __('Part List Item') ||
          node.data.type == __('Product Bundle Item')
        );
      },
      click: function (node) {
        window.open('/app/item/' + JSON.parse(node.data.value).value);
      },
      btnClass: 'hidden-xs',
    },
    {
      label: __('Edit Part List'),
      condition: function (node) {
        return node.data.type == __('Part List');
      },
      click: function (node) {
        window.open('/app/part-list/' + JSON.parse(node.data.value).value);
      },
      btnClass: 'hidden-xs',
    },
    {
      label: __('Open Product Bundle'),
      condition: function (node) {
        return (
          node.data.type == __('Product Bundle') ||
          node.data.type == __('Variant Item / Product Bundle')
        );
      },
      click: function (node) {
        window.open('/app/product-bundle/' + JSON.parse(node.data.value).value);
      },
      btnClass: 'hidden-xs',
    },
  ],
  // enable custom buttons beside each node
  extend_toolbar: false,
};

function pushFiltersToUrl(treeview) {
  var treeview = treeview || frappe.treeview_settings['Item Explorer'].treeview;

  var pc = treeview.args.product_category;
  var ic = treeview.args.item_code;
  var pn = treeview.args.product_name;

  const queryParams = new URLSearchParams(window.location.search);
  if (pc) queryParams.set('product_category', pc); else queryParams.delete('product_category');
  if (ic) queryParams.set('item_code', ic); else queryParams.delete('item_code');
  if (pn) queryParams.set('product_name', pn); else queryParams.delete('product_name');

  const newUrl = `${window.location.pathname}${queryParams ? "?" + queryParams.toString() : ""}`;
  window.history.pushState(null, '', newUrl);
  const newFilter = pn || ic || pc
  if (treeview.root_label !== newFilter) {
    treeview.root_label = newFilter;
    console.log(treeview.root_label)
  };
}