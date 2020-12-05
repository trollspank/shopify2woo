"""
We must track and build each order, shopify lists every line as an "order", but if the order # matches the one before
it, then it's actually just a line item ON that order, not a brand new order. WooCommerce, however, does not accept
that reality, they want a single sell to have all the line items (either with pipes or in JSON format).

We will encode all line items as JSON within the "line items" cell, as defined by WooCommerce's example CSV file
format: https://docs.google.com/spreadsheets/d/16ub-_xEJD9V5UL6d_rTQ4LLu0PT9jXJ0Ti-iirlKyuU/edit#gid=584795629

A not about line_items, which we will encoding in our CSV "cell" as a JSON array: we are going to pull in the
bare minimum to make this work well, for instance:

[{
    "sku": "560",
    "quantity": "1",
    "total": "32.99"
}]

I ran into issues importing the 'name' because names that contain any quotes are encoded with a \" and this causes
the CSV Importer heartburn. It should work (it's formatted right) but it doesn't. So, names like:
   8" Hardwood Muddler translate to "8\" Hardwood Muddler" and the system fails to parse SKU's after it encounters
   a \"

One could use the | delimited option instead of JSON (from the example CSV file) however, if your product name
contains a | (like "8 inch hardwood muddler | basic bartool") then you may run into more problems. However, given
the system does not even use the name, but instead favors the SKU to pull the product right from the product
database (as I've tested) the name does nothing but creates more import difficulties. So, we are leaving it off.
"""

import json

# My custom imports
import fields
from utils import split_name


class Order:

    def __init__(self, record):
        """
        Initialize a new order with all the base information plus one line item.

        Parameters
        ----------
        record: A CSV record row (see 'csv' module)
        """
        self._order = record[fields.name].replace("#", "")
        self._status = "completed"                       # Only bring in completed orders
        self._created_at = record[fields.created_at]
        self._total = record[fields.total]
        self._cart_tax = record[fields.tax_1_value]
        self._total_shipping = record[fields.shipping]
        self._total_discount = record[fields.discount_amount]
        self._payment_method = record[fields.payment_method]
        self._currency = record[fields.currency]
        self._billing_first_name, self._billing_last_name = split_name(record[fields.billing_name])
        self._billing_email = record[fields.email]
        self._billing_address_1 = record[fields.billing_address1]
        self._billing_address_2 = record[fields.billing_address2]
        self._billing_phone = record[fields.billing_phone]
        # Note, odd shopify bug in zipcodes, some start with a ' mark for some reason, so remove that in both
        # postalcode fields.
        self._billing_postcode = record[fields.billing_zip].replace("'", "")
        self._billing_city = record[fields.billing_city]
        self._billing_state = record[fields.billing_province]
        self._billing_country = record[fields.billing_country]
        self._billing_company = record[fields.billing_company]
        self._shipping_first_name, self._shipping_last_name = split_name(record[fields.shipping_name])
        self._shipping_address_1 = record[fields.shipping_address1]
        self._shipping_address_2 = record[fields.shipping_address2]
        self._shipping_postcode = record[fields.billing_zip].replace("'", "")
        self._shipping_city = record[fields.shipping_city]
        self._shipping_state = record[fields.shipping_province]
        self._shipping_country = record[fields.shipping_country]
        self._shipping_company = record[fields.shipping_company]
        self._note = record[fields.notes]

        self._shipping_lines = [{
            "method_title": record[fields.shipping_method],
            "total": record[fields.shipping]
        }]

        # Add initial item from this record (more can follow)
        self._item_list = list()
        self.add_item(record)

    def dump(self):
        """
        Dump order out in a readable display for debugging.

        Returns
        -------
        None.
        """
        print(f"Order: {self._order}")
        print(f"Item List: %s" % (json.dumps(self._item_list)))

    def add_item(self, record):
        """
        Add a new item to our list of items that this order can have on it, we'll store as a dictionary because
        later we'll need to render it as a JSON array, so that will make it easy.

        :param record: the CSV record array
        :return: None.
        """
        # Note: We will not pull along the name of the item, the SKU will do because it will pull
        # the relevant item data from the product data in WooCommerce (which should be entered before
        # the orders).
        # If the product SKU isn't found (and you force it via import to include anyway) the item name
        # still isn't used (the item will just say "Unknown Product").
        item = {
            "sku": record[fields.lineitem_sku],
            "quantity": record[fields.lineitem_quantity],
            "total": record[fields.lineitem_price],
        }

        self._item_list.append(item)

    def build_record(self):
        """
        Build an array appropriate for a CSV writer to writerow() to disk. The order makes a big
        difference here because it must match the column header that was written down (if it was
        written).

        :return: entire product class written into an ordered array (order matters)
        """
        return [
            self._order,
            self._created_at,
            self._status,
            self._total,
            self._total_shipping,
            self._cart_tax,
            # skip shipping_tax (on purpose, because we don't have that record)
            self._total_discount,
            # skip total discount (shopify doesn't give us that easily)
            self._payment_method,
            self._currency,
            # skip customer_id because we don't have that
            self._billing_first_name,
            self._billing_last_name,
            self._billing_email,
            self._billing_phone,
            self._billing_address_1,
            self._billing_address_2,
            self._billing_postcode,
            self._billing_city,
            self._billing_state,
            self._billing_country,
            self._billing_company,
            self._shipping_first_name,
            self._shipping_last_name,
            self._shipping_address_1,
            self._shipping_address_2,
            self._shipping_postcode,
            self._shipping_city,
            self._shipping_state,
            self._shipping_country,
            self._shipping_company,
            self._note,
            # Line items (JSON)
            json.dumps(self._item_list),
            # Shipping lines (JSON)
            json.dumps(self._shipping_lines),
            # We will skip tax_lines, coupon_lines, refunds, order_notes, download_permissions_granted, order_cost_total
        ]
