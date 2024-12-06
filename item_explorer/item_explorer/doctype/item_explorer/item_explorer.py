import frappe
from frappe.utils.nestedset import NestedSet
from frappe.utils import json
from frappe import _

class ItemExplorer(NestedSet):

	def db_insert(self, *args, **kwargs):
		pass

	def load_from_db(self):
		pass

	def db_update(self, *args, **kwargs):
		pass

	@staticmethod
	def get_list(args):
		pass

	@staticmethod
	def get_count(args):
		pass

	@staticmethod
	def get_stats(args):
		pass

@frappe.whitelist()
def get_children(parent=None, product_category=None, item_code=None, product_name=None):
	# Check if 'parent' is None, empty, or invalid JSON
	if parent and parent.strip():  # Only load JSON if 'parent' is a non-empty string
		try:
			parent_object = json.loads(parent)
		except json.JSONDecodeError:
            # Handle case where parent is an invalid JSON string but defined
			parent_object = {"value": parent, "type": "filter"}
	else:
		# Fallback if 'parent' is None or empty
		parent_object = {"value": "", "type": ""}
	parent_value = parent_object["value"]
	parent_type = parent_object["type"]	

	# Top Level filtering
	if parent_type == "filter": 
		# if item code is set, this filter takes precedence
		if item_code:
			return get_items(list_filters=[["name", "=", item_code]])
		
		# product name filters allow for searching for multiple words
		if product_name:			
			return get_product_name_filter_results(product_name)
		
		# only if the two filters are empty will the hierarchy be loaded
		return get_top_level_categories(product_category) # category filter set
	elif parent_value == "":
		return get_top_level_categories(product_category) # root level no items here since we put them in "others"
	
	# Virtual Category for all uncategorized items
	elif parent_value == "others":
		if parent_type == _("Bundles Folder"):
			return get_bundle_items(parent_category="other")
		else:
			return get_items_in_others()
			
	# Parent value is defined -> load children
	elif parent_value:
		if parent_type == _("Category"):
			child_categories = get_product_categories([["parent_product_category", "=", parent_value]])
			items = get_items(parent_category=parent_value)
			return child_categories + items
		elif parent_type == _("Parent Item"):
			variant_items = get_variants(parent_item=parent_value)
			part_lists = get_part_lists([parent_value])
			return variant_items
		elif parent_type == _("Item") or parent_type == _("Item Variant"):
			part_lists = get_part_lists([parent_value])
			return part_lists
		elif parent_type == _("Part List"):
			items = get_part_list_items(parent_value)
			for item in items:
				item["type"] = _("Part List Item")
			return items
		elif parent_type == _("Product Bundle") or parent_type == _("Item Variant / Product Bundle"):
			part_lists = get_part_lists([parent_value])
			return get_product_bundle_items(parent_value) + part_lists
		elif parent_type == _("Bundles Folder"):
			return get_bundle_items(parent_category=parent_value)


def get_top_level_categories(category_filter):
	if(category_filter):
		categories = get_product_categories([["name", "=", category_filter]])
		return categories
	
	categories = get_product_categories([["parent_product_category", "=", ""]])
	items = get_items(parent_category=None)

	# add a top level category to catch all uncategorized items
	if (len(items)) > 0:
		categories.append({
			"value": json.dumps({ "value": "others", "type": _("Category") }),
			"title": _("Others"),
			"expandable": True,
			"parent": "",
			"image_url": "",
			"type": _("Category")
		})
		# assign item to new parent "others"
		for item in items:
			item["parent"] = "others"

	return categories

def get_items(parent_category=None, list_filters=None):
	if list_filters:
		items = frappe.get_list(
			"Item",
			fields=["name", "is_stock_item", "item_name as title", "has_variants as expandable", "variant_of as parent", "custom_product_category as product_category", "image as image_url"],
			filters=list_filters,
			order_by="item_name",
		)
	else:
		items = get_items_by_parent_category(parent_category)

	# get part lists for all items in filters
	# so we know if we can expand the item further
	items = set_expandable(items)
	items = set_image_url(items)
	items = add_stock_levels(items)
	items = add_bundles_folder(items, parent_category)

	items = add_value_json_field(items)

	return items

def get_bundle_items(parent_category=None):
	bundles = []
	if parent_category == "other" or not(parent_category):
		# nearly identical as the above query, except the part for filtering by custom_product_category
		bundles = frappe.db.sql("""
			SELECT name, item_name as title, has_variants as expandable, variant_of as parent, custom_product_category as product_category, image as image_url
			FROM tabItem
			WHERE 
				disabled = 0 
				AND (variant_of = '' OR variant_of IS NULL) 
				AND (custom_product_category = '' OR custom_product_category IS NULL)
				
				# exclude items that are part of a Part List
				# AND name NOT IN (
				# 	SELECT pli.item_code FROM `tabPart List Item` pli
				# 	JOIN `tabPart List` pl ON pli.parent = pl.name
				# 	WHERE pl.docstatus = 1
				# )
						
				# exclude items that are part of a Product Bundle
				AND name NOT IN (
					SELECT pbi.item_code FROM `tabProduct Bundle Item` pbi
					JOIN `tabProduct Bundle` pb ON pbi.parent = pb.new_item_code
					WHERE pb.disabled = 0
				)
				
				# only include items that are a Product Bundle, these will be included under a separate subfolder "Bundles"
				AND name IN (
					SELECT pb.new_item_code FROM `tabProduct Bundle` pb
					WHERE pb.disabled = 0
				)
			ORDER BY item_name
		""", as_dict=True)
	else:
		bundles = frappe.db.sql("""
			SELECT name, item_name as title, has_variants as expandable, variant_of as parent, custom_product_category as product_category, image as image_url
			FROM tabItem
			WHERE 
				disabled = 0 
				AND (variant_of = '' OR variant_of IS NULL) 
				AND custom_product_category = %(filter_value)s
				
				# exclude items that are part of a Part List
				# AND name NOT IN (
				# 	SELECT pli.item_code FROM `tabPart List Item` pli
				# 	JOIN `tabPart List` pl ON pli.parent = pl.name
				# 	WHERE pl.docstatus = 1
				# )
						
				# exclude items that are part of a Product Bundle
				AND name NOT IN (
					SELECT pbi.item_code FROM `tabProduct Bundle Item` pbi
					JOIN `tabProduct Bundle` pb ON pbi.parent = pb.new_item_code
					WHERE pb.disabled = 0
				)
				
				# only include items that are a Product Bundle, these will be included under a separate subfolder "Bundles"
				AND name IN (
					SELECT pb.new_item_code FROM `tabProduct Bundle` pb
					WHERE pb.disabled = 0
				)
			ORDER BY item_name
		""", values={"filter_value": parent_category}, as_dict=True)

	bundles = set_expandable(bundles)
	bundles = set_image_url(bundles)
	bundles = add_stock_levels(bundles)
	bundles = add_value_json_field(bundles)

	return bundles

def get_variants(parent_item):
	items = get_items_by_parent_item(parent_item)
	items = set_variants_expandable(items)
	items = add_stock_levels(items)
	items = add_value_json_field(items)
	return items;
	
def add_value_json_field(items):
	for item in items:
		item["value"] = json.dumps({ "value": item["name"] if "name" in item else "", "stock_current": item["stock_current"] if "stock_current" in item else "", "type": item["type"], "image_url": item["image_url"] if "image_url" in item else ""})
	return items

def get_part_lists(item_names):
	if(len(item_names) == 0):
		return []
	part_lists = frappe.db.sql("""
		-- get both the entries from the current replacement part field and the product history fields
		SELECT pl.title, pvh.product_version, pvh.replacement_part_list as name, i.item_code AS parent, (i.custom_replacement_part_list = pvh.replacement_part_list) AS is_current, pl.creation, i.image as image_url
		FROM tabItem i
		JOIN `tabItem Product Version History` pvh ON i.`name` = pvh.parent
		JOIN `tabPart List` pl ON pvh.replacement_part_list = pl.`name`
		LEFT JOIN `tabProduct Version Compatibility` pvc ON pl.`name` = pvc.parent
		WHERE pl.is_active = 1 AND pl.part_list_type = 'Replacement Part List'
		AND i.item_code IN %(filter_value)s

		UNION

		SELECT pl.title, i.custom_product_version, i.custom_replacement_part_list as name, i.item_code AS parent, 1 AS is_current, pl.creation, i.image as image_url
		FROM tabItem i
		JOIN `tabPart List` pl ON i.custom_replacement_part_list = pl.`name`
		LEFT JOIN `tabProduct Version Compatibility` pvc ON pl.`name` = pvc.parent
		WHERE pl.is_active = 1 AND pl.part_list_type = 'Replacement Part List'
		AND i.item_code IN %(filter_value)s

		ORDER BY creation
			   """, values={"filter_value": item_names}, as_dict=True)
	
	for part_list in part_lists:
		part_list["expandable"] = True
		part_list["type"] = _("Part List")
		part_list["title"] = _("Part List | ") + (( part_list["product_version"] + " | ") if part_list["product_version"] else " ") + part_list["creation"].strftime("%Y-%m-%d")
		
	part_lists = add_value_json_field(part_lists)

	return part_lists

def get_part_list_items(part_list):
	if(len(part_list) == 0):
		return []
	items = frappe.db.sql("""
		SELECT 
			pli.part_number, 
			pli.quantity, 
			pli.part AS name,
			i.item_name as title,
			i.image as image_url
		FROM 
			`tabPart List Item` pli
		LEFT JOIN tabItem i ON i.`name` = pli.part
		WHERE 
			pli.parent = %(filter_value)s
		ORDER BY 
			pli.idx 
	""", values={"filter_value": part_list}, as_dict=True)
	
	for item in items:
		part_number = item["part_number"] if item["part_number"] else None
		circled_num = f'<span style="display: inline-block; width: 24px; height: 24px; border-radius: 50%; background-color: black; color: white; text-align: center; line-height: 24px;">{part_number}</span> ' if part_number else ""
		
		# Modify the title field to include the circled number and quantity
		item["title"] = f"{circled_num}{item['quantity']}x {item['title']}"
		item["type"] = _("Item")  # Add the 'type' field

	# Add additional JSON field if needed (assumed this function does extra processing)
	items = add_stock_levels(items)
	items = add_value_json_field(items)
	return items

def get_product_bundles(item_names):
	# construct filter for product bundles
	filters = [["disabled", "=", 0]]
	filters.append(["new_item_code", "in", item_names])
	
	bundles = frappe.get_list(
		"Product Bundle",
		fields=["name", "new_item_code as title", "new_item_code as parent", "custom_image as image_url"],
		filters=filters,
		order_by="new_item_code",
	)

	for bundle in bundles:
		bundle["expandable"] = True
		bundle["type"] = _("Product Bundle")
		bundle["title"] = _("Product Bundle") + " " + bundle["title"]

	bundles = add_stock_levels(bundles)
	bundles = add_value_json_field(bundles)

	return bundles

def get_product_bundle_items(item_name):
	bundles = get_product_bundles([item_name])
	if len(bundles) == 0:
		return []
	
	items = frappe.get_all(
		"Product Bundle Item",
		fields=["item_code as name", "description as title", "qty as quantity"],
		filters=[["parent", "=", bundles[0]["name"]]],
		order_by="idx",
	)
	for item in items:
		item["type"] = _("Product Bundle Item")

	items = set_expandable(items)
	items = set_image_url(items)
	items = add_stock_levels(items)
	items = add_value_json_field(items)

	return items
	
def get_product_categories(filters):
	categories = frappe.get_list(
		"Product Category",
		fields=["name", "title", "parent_product_category as parent", "is_group as expandable"],
		filters=filters,
		order_by="title",
	)
	for category in categories:
		category["expandable"] = True
		category["type"] = _("Category")
	
	categories = add_value_json_field(categories)

	return categories

def get_product_name_filter_results(product_name):
	product_name_filters = []
	categories_filters = []
	for product_name_word in product_name.split(" "):
		product_name_filters.append(["item_name", "like", "%" + product_name_word + "%"])
		categories_filters.append(["title", "like", "%" + product_name_word + "%"])

	categories = get_product_categories(categories_filters)
	items = get_items(list_filters=product_name_filters)
	set_image_url(items)
	return categories + items

def get_items_in_others():
	items = get_items(parent_category=None) # others level -> uncategorized items
	for item in items:
		item["parent"] = "others"	

	return items

def add_bundles_folder(items, parent_category=None):
	bundles = get_bundle_items(parent_category)
	if len(bundles) > 0:
		parent = parent_category if parent_category else 'others'
		items.append({
			"name": parent,
			"title": "Bundles",
			"expandable": True,
			"parent": parent,
			"image_url": "",
			"type": _("Bundles Folder")
		})

	return items

def add_stock_levels(items):
	item_names = [item["name"] for item in items]
	bundle_items = frappe.get_all(
		"Product Bundle Item",
		fields=["item_code as name", "qty as quantity", "parent"],
		filters=[["parent", "in", item_names]],
		order_by="idx",
	)
	bundle_item_names = [bundle_item["name"] for bundle_item in bundle_items]
	all_related_item_names = item_names + bundle_item_names
	stock_levels = frappe.get_all(
		"Bin",
		fields=["item_code", "actual_qty"],
		filters=[["item_code", "in", all_related_item_names]],
	)
	
	for item in items:
		if(item["type"] == _("Product Bundle") or item["type"] == _("Item Variant / Product Bundle")):
			item = set_bundle_stock_level(item, bundle_items, stock_levels)
		else:
			for stock_level in stock_levels:
				if item["name"] == stock_level["item_code"]:
					item["stock_current"] = item["stock_current"] + stock_level["actual_qty"] if "stock_current" in item else stock_level["actual_qty"]

	return items

def set_bundle_stock_level(item, bundle_items, stock_levels):
	_bundle_items = [bundle_item for bundle_item in bundle_items if bundle_item["parent"] == item["name"]]
	item["stock_current"] = None
	sum_stock_levels = {}

	for stock_level in stock_levels:
		item_code = stock_level["item_code"]
		frappe.msgprint(f"stock level item code: {item_code} (should be same)")
		sum_stock_levels[item_code] = sum_stock_levels[item_code] + stock_level["actual_qty"] if sum_stock_levels.get(item_code) != None else stock_level["actual_qty"]

	for _bundle_item in _bundle_items:
		bundle_item_sku = _bundle_item["name"]
		bundle_item_qty = _bundle_item["quantity"] if _bundle_item["quantity"] != 0 else 1 # ensure not dividing by zero later
		stock = sum_stock_levels[bundle_item_sku] if sum_stock_levels.get(bundle_item_sku) != None else 0

		possible_item_qty = stock / bundle_item_qty
		item["stock_current"] = possible_item_qty if item["stock_current"] == None or possible_item_qty < item["stock_current"] else item["stock_current"]
	
	return item

def set_image_url(items):
	item_names = []
	for item in items:
		if "image_url" in item and item["image_url"] != "" and item["image_url"] != None:
			continue;
		item_names.append(item["name"])

	files = frappe.get_all(
		"File",
		fields=["attached_to_name as item_code", "file_url"],
		filters=[["attached_to_field", "like", "%image"],["attached_to_name", "in", item_names]],
	)

	for item in items:	
		if "image_url" in item and item["image_url"] != "" and item["image_url"] != None:
			continue;
		for file in files:
			try:
				if file["item_code"] == item["name"]:
					item["image_url"] = file["file_url"]
			except:
				pass

	return items

	
def set_expandable(items):
	item_names = [item["name"] for item in items]
	related_part_lists = get_part_lists(item_names)
	related_bundles = get_product_bundles(item_names)

	# make part lists and bundles expandable and modify type
	for item in items:
		if(not "expandable" in item):
			item["expandable"] = False

		item["type"] = _("Parent Item") if item["expandable"] == 1 else _("Item")
		for part_list in related_part_lists:
			try:
				if part_list["parent"] == item["name"]:
					item["expandable"] = True
			except:
				pass

		for bundle in related_bundles:
			try:
				if bundle["parent"] == item["name"]:
					item["expandable"] = True
					item["type"] = _("Product Bundle")
			except:
				pass

	

	return items
	
def set_variants_expandable(items):
	item_names = []
	for item in items:
		item_names.append(item["name"])
	part_lists = get_part_lists(item_names)
	bundles = get_product_bundles(item_names)

	for item in items:
		if(not "expandable" in item):
			item["expandable"] = False		
		
		item["type"] = _("Item Variant")

		for part_list in part_lists:
			try:
				if part_list["parent"] == item["name"]:
					item["expandable"] = True
			except:
				pass

		for bundle in bundles:
			try:
				if bundle["parent"] == item["name"]:
					item["expandable"] = True
					item["type"] = _("Item Variant / Product Bundle")
			except:
				pass

	return items



def get_items_by_parent_category(parent_category):
	if parent_category: # get descendants of a category
		items = frappe.db.sql("""
			SELECT name, item_name as title, has_variants as expandable, variant_of as parent, custom_product_category as product_category, image as image_url
			FROM tabItem
			WHERE 
				disabled = 0 
				AND (variant_of = '' OR variant_of IS NULL) 
				AND custom_product_category = %(filter_value)s
						
				# exclude items that are part of a Product Bundle
				AND name NOT IN (
					SELECT pbi.item_code FROM `tabProduct Bundle Item` pbi
					JOIN `tabProduct Bundle` pb ON pbi.parent = pb.new_item_code
					WHERE pb.disabled = 0
				)
				
				# exclude items that are a Product Bundle, these will be included under a separate subfolder "Bundles"
				AND name NOT IN (
					SELECT pb.new_item_code FROM `tabProduct Bundle` pb
					WHERE pb.disabled = 0
				)
			ORDER BY item_name
		""", values={"filter_value": parent_category}, as_dict=True)
	else: # get uncategorized items
		items = frappe.db.sql("""
			SELECT name, item_name as title, has_variants as expandable, variant_of as parent, custom_product_category as product_category, image as image_url
			FROM tabItem
			WHERE 
				disabled = 0 
				AND (variant_of = '' OR variant_of IS NULL) 
				AND (custom_product_category = '' OR custom_product_category IS NULL)
						
				# exclude items that are part of a Product Bundle
				AND name NOT IN (
					SELECT pbi.item_code FROM `tabProduct Bundle Item` pbi
					JOIN `tabProduct Bundle` pb ON pbi.parent = pb.new_item_code
					WHERE pb.disabled = 0
				)
					
				# exclude items that are a Product Bundle, these will be included under a separate subfolder "Bundles"
				AND name NOT IN (
					SELECT pb.new_item_code FROM `tabProduct Bundle` pb
					WHERE pb.disabled = 0
				)
			ORDER BY item_name
		""", as_dict=True)

	return items

def get_items_by_parent_item(parent_item):
	items = frappe.db.sql("""
		SELECT name, item_name as title, variant_of as parent, custom_product_category as product_category, image as image_url
		FROM tabItem
		WHERE 
			disabled = 0 
			AND variant_of = %(parent_item)s
		ORDER BY item_name
	""", values={"parent_item": parent_item}, as_dict=True)

	return items