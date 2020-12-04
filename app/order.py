"""
We must track and build each order, shopify lists every line as an "order", but if the order # matches the one before
it, then it's actually just a line item ON that order, not a brand new order. WooCommerce, however, does not accept
that reality, they want a single sell to have all the line items (either with pipes or in JSON format).

We will encode all line items as JSON within the "line items" cell, as defined by WooCommerce's example CSV file
format: https://docs.google.com/spreadsheets/d/16ub-_xEJD9V5UL6d_rTQ4LLu0PT9jXJ0Ti-iirlKyuU/edit#gid=584795629

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
        self._order = record[fields.name]
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

        self._shipping_lines = {
            "method_title": record[fields.shipping_method],
            "total": record[fields.shipping]
        }

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
        item = {
            "sku": record[fields.lineitem_sku],
            "quantity": record[fields.lineitem_quantity],
            "name": record[fields.lineitem_name],
            "total": record[fields.lineitem_price],
        }
        self._item_list.append(item)
