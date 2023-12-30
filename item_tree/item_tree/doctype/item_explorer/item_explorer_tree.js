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
  
      let accounts = [];
      if (deep) {
        // in case of `get_all_nodes`
        accounts = nodes.reduce((acc, node) => [...acc, ...node.data], []);
      } else {
        accounts = nodes;
      }
  
      frappe.db.get_list("Item", ).then((value) => {
        if(value) {
  
          const get_balances = frappe.call({
            method: 'erpnext.accounts.utils.get_account_balances',
            args: {
              accounts: accounts,
              company: cur_tree.args.company
            },
          });
  
          get_balances.then(r => {
            if (!r.message || r.message.length == 0) return;
  
            for (let account of r.message) {
  
              const node = cur_tree.nodes && cur_tree.nodes[account.value];
              if (!node || node.is_root) continue;
  
              // show Dr if positive since balance is calculated as debit - credit else show Cr
              const balance = account.balance_in_account_currency || account.balance;
              const dr_or_cr = balance > 0 ? "Dr": "Cr";
              const format = (value, currency) => format_currency(Math.abs(value), currency);
  
              if (account.balance!==undefined) {
                node.parent && node.parent.find('.balance-area').remove();
                $('<span class="balance-area pull-right">'
                  + (account.balance_in_account_currency ?
                     (format(account.balance_in_account_currency, account.account_currency) + " / ") : "")
                  + format(account.balance, account.company_currency)
                  + " " + dr_or_cr
                  + '</span>').insertBefore(node.$ul);
              }
            }
          });
        }
      });
    },
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
