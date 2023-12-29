// in Frappe JS files you can use jQuery 2

frappe.pages['item-tree'].on_page_load = function (wrapper) {
  var page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Item Tree',
    single_column: true,
  });

  page.set_title('Item Explorer');
  page.args = {
    item_code: null,
  };

  page.parent_item_field = page.add_field({
    fieldname: 'item_code',
    label: __('Parent Item'),
    fieldtype: 'Link',
    options: 'Item',
    filters: { has_variants: 1 },
    default: frappe.route_options && frappe.route_options.item_code,
    change: function () {
      page.refresh();
    },
  });

  // page.sort_selector = new frappe.ui.SortSelector({
  //   parent: page.wrapper.find('.page-form'),
  //   args: {
  //     sort_by: 'projected_qty',
  //     sort_order: 'asc',
  //     options: [
  //       { fieldname: 'projected_qty', label: __('Projected qty') },
  //       { fieldname: 'reserved_qty', label: __('Reserved for sale') },
  //       {
  //         fieldname: 'reserved_qty_for_production',
  //         label: __('Reserved for manufacturing'),
  //       },
  //       {
  //         fieldname: 'reserved_qty_for_sub_contract',
  //         label: __('Reserved for sub contracting'),
  //       },
  //       { fieldname: 'actual_qty', label: __('Actual qty in stock') },
  //     ],
  //   },
  //   change: function (sort_by, sort_order) {
  //     console.log(sort_order);
  //     page.args.sort_by = sort_by;
  //     page.args.sort_order = sort_order;
  //     page.args.start = 0;
  //     page.refresh();
  //   },
  // }
  // );

  // You can style individual elements like this
  // altenatively you can use a .css file with the same name as this file
  // page.sort_selector.wrapper.css({
  //   'margin-right': '15px',
  //   'margin-top': '4px',
  // });

  page.render = function () {
    // Alternatively you could get the fields individually
    // page.args.item_code = page.parent_item_field.get_value();
    page.args = page.get_form_values();

    // Get data
    frappe
      .call({
        method: 'item_tree.item_tree.page.item_tree.item_tree.get_data',
        args: page.args,
      })
      .then(data => {
        $(
          frappe.render_template('item_tree', {
            data: JSON.stringify(data.message),
          })
        ).appendTo(page.body);
      });
  };

  page.refresh = () => {
    page.args = page.get_form_values();
    updateUrl(page.args);

    // console.log('page in refresh', page.args);
    page.render();
  };

  page.render();
};

function updateUrl(args) {
  const currentRoute = frappe.get_route();
  const url = new URLSearchParams();

  for (let key in args) {
    const value = args[key];
    if (value) {
      url.append(key, value);
    }
  }

  const queryParams = url.toString();
  history.pushState(
    {},
    '',
    currentRoute + (queryParams ? `?${queryParams}` : '')
  );
}
