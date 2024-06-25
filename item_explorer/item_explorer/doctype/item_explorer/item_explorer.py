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

	parent_object = json.loads(parent) if parent else { "value": "", "type": "" }
	parent_value = parent_object["value"]
	parent_type = parent_object["type"]	

	# Top Level
	if parent_value == "": 
		# if item code is set, this filter takes precedence
		if item_code:
			return get_items(list_filters=[["name", "=", item_code]])
		
		# product name filters allow for searching for multiple words
		if product_name:			
			return get_product_name_filter_results(product_name)
		
		# only if the two filters are empty will the hierarchy be loaded
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
			boms = get_boms([parent_value])
			return variant_items
		elif parent_type == _("Item") or parent_type == _("Item Variant"):
			boms = get_boms([parent_value])
			return boms
		elif parent_type == _("BOM"):
			items = get_bom_items(parent_value)
			for item in items:
				item["type"] = _("BOM Item")
			return items
		elif parent_type == _("Product Bundle") or parent_type == _("Item Variant / Product Bundle"):
			return get_product_bundle_items(parent_value)
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
			fields=["name", "item_name as title", "has_variants as expandable", "variant_of as parent", "custom_product_category as product_category", "image as image_url"],
			filters=list_filters,
			order_by="item_name",
		)
	else:
		items = get_items_by_parent_category(parent_category)

	# get boms for all items in filters
	# so we know if we can expand the item further
	items = set_expandable(items)
	items = set_image_url(items)
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
				
				# exclude items that are part of a BOM
				# AND name NOT IN (
				# 	SELECT bi.item_code FROM `tabBOM Item` bi
				# 	JOIN `tabBOM` b ON bi.parent = b.name
				# 	WHERE b.docstatus = 1
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
				
				# exclude items that are part of a BOM
				# AND name NOT IN (
				# 	SELECT bi.item_code FROM `tabBOM Item` bi
				# 	JOIN `tabBOM` b ON bi.parent = b.name
				# 	WHERE b.docstatus = 1
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
	bundles = add_value_json_field(bundles)

	return bundles

def get_variants(parent_item):
	items = get_items_by_parent_item(parent_item)
	items = set_variants_expandable(items)
	items = add_value_json_field(items)
	return items;
	
def add_value_json_field(items):
	for item in items:
		item["value"] = json.dumps({ "value": item["name"] if "name" in item else "", "type": item["type"], "image_url": item["image_url"] if "image_url" in item else ""})
	return items

def get_boms(item_names):
	# construct filter for boms
	filters = [["docstatus", "=", 1], ["is_active", "=", 1]]
	filters.append(["item", "in", item_names])
	
	boms = frappe.get_list(
		"BOM",
		fields=["name", "item_name as title", "item as parent", "is_default", "custom_version", "creation", "image as image_url"],
		filters=filters,
		order_by="creation desc",
	)
	for bom in boms:
		bom["expandable"] = True
		bom["type"] = _("BOM")
		bom["title"] = _("Part List | ") + (( "v" + bom["custom_version"] + " | ") if bom["custom_version"] else " ") + bom["creation"].strftime("%Y-%m-%d")
		if bom["is_default"] == 1:
			bom["title"] = bom["title"] +  " (" + _("Default") + ")"
		
	boms = add_value_json_field(boms)

	return boms

def get_bom_items(bom):
	items = frappe.get_all(
		"BOM Item",
		fields=["item_code as name", "item_name as title", "image as image_url"],
		filters=[["docstatus", "=", 1], ["parent", "=", bom]],
		order_by="idx",
	)
	for item in items:
		item["type"] = _("Item")
	
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

	bundles = add_value_json_field(bundles)

	return bundles

def get_product_bundle_items(item_name):
	bundles = get_product_bundles(item_name)
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

	items = set_image_url(items)
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
	item_names = []
	for item in items:
		item_names.append(item["name"])
	related_boms = get_boms(item_names)
	related_bundles = get_product_bundles(item_names)

	# make boms and bundles expandable and modify type
	for item in items:
		item["type"] = _("Parent Item") if item["expandable"] == 1 else _("Item")
		for bom in related_boms:
			try:
				if bom["parent"] == item["name"]:
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
	boms = get_boms(item_names)
	bundles = get_product_bundles(item_names)

	for item in items:
		item["type"] = _("Item Variant")
		for bom in boms:
			try:
				if bom["parent"] == item["name"]:
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
				
				# exclude items that are part of a BOM
				# AND name NOT IN (
				# 	SELECT bi.item_code FROM `tabBOM Item` bi
				# 	JOIN `tabBOM` b ON bi.parent = b.name
				# 	WHERE b.docstatus = 1
				# )
						
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
				
				# exclude items that are part of a BOM		
				# AND name NOT IN (
				# 	SELECT bi.item_code FROM `tabBOM Item` bi
				# 	JOIN `tabBOM` b ON bi.parent = b.name
				# 	WHERE b.docstatus = 1
				# )
						
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
			
			# disabled because it hides items that themselves are part of their BOM
			# exclude items that are part of a BOM
			# AND name NOT IN (
			# 	SELECT bi.item_code FROM `tabBOM Item` bi
			# 	JOIN `tabBOM` b ON bi.parent = b.name
			# 	WHERE b.docstatus = 1
			# )
		ORDER BY item_name
	""", values={"parent_item": parent_item}, as_dict=True)

	return items