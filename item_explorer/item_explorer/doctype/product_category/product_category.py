# Copyright (c) 2023, formbench and contributors
# For license information, please see license.txt

# import frappe
from frappe.utils.nestedset import NestedSet

class ProductCategory(NestedSet):
    def autoname(self):
        name = self.title
        name = name.replace("&", "")
        name = name.replace("  ", "-")
        name = name.replace(" ", "-")
        name = name.replace("ß", "ss")
        name = name.replace("ü", "ue")
        name = name.replace("ä", "ae")
        name = name.replace("ö", "oe")
        name = name.replace("/", "")
        name = name.replace("--", "-")
        name = name.lower()
        self.name = name

