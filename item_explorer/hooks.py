app_name = "item_explorer"
app_title = "Item Explorer"
app_publisher = "formbench GmbH"
app_description = "Explore Variant Items hierarchically"
app_email = "tech@formbench.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/item_explorer/css/item_explorer.css"
# app_include_js = "/assets/item_explorer/js/item_explorer.js"

# include js, css files in header of web template
# web_include_css = "/assets/item_explorer/css/item_explorer.css"
# web_include_js = "/assets/item_explorer/js/item_explorer.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "item_explorer/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "item_explorer.utils.jinja_methods",
#	"filters": "item_explorer.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "item_explorer.install.before_install"
# after_install = "item_explorer.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "item_explorer.uninstall.before_uninstall"
# after_uninstall = "item_explorer.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "item_explorer.utils.before_app_install"
# after_app_install = "item_explorer.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "item_explorer.utils.before_app_uninstall"
# after_app_uninstall = "item_explorer.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "item_explorer.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"item_explorer.tasks.all"
#	],
#	"daily": [
#		"item_explorer.tasks.daily"
#	],
#	"hourly": [
#		"item_explorer.tasks.hourly"
#	],
#	"weekly": [
#		"item_explorer.tasks.weekly"
#	],
#	"monthly": [
#		"item_explorer.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "item_explorer.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "item_explorer.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "item_explorer.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["item_explorer.utils.before_request"]
# after_request = ["item_explorer.utils.after_request"]

# Job Events
# ----------
# before_job = ["item_explorer.utils.before_job"]
# after_job = ["item_explorer.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"item_explorer.auth.validate"
# ]
