"""Shopify2Woo
The objective of Shopify2Woo is to read in a Shopify order export CSV file (exported in Excel dialect)
and convert it into a file appropriate for importing into WooCommerce using the Import Orders CVS addon.

The guidance for the CSV import manipulation is based on the instructions on Importing orders written
by Simon Gondeck:
https://sgwebpartners.com/how-to-migrate-shopify-customers-and-orders-to-woocommerce/

Unfortunately WooCommerce does not come with the ability to import orders and customers "out of the box"
without spending more money.
"""

# Required Imports
import click
import csv

# My custom imports
import fields
from utils import split_name


@click.command()
@click.argument("input_csv", type=click.File('r'))
@click.argument("output_csv", type=click.File('w'))
def cli(input_csv, output_csv):
    """
    Entry point for executing the base functionality for shopify2woo, this sucker will take the CSV file
    of data from Shopify and burp out an output CSV that can be imported into WooCommerce.

    Parameters
    ----------
    input_csv: the csv file from Shopify
    output_csv: the new csv file for WooCommerce

    Returns
    -------

    """
    # Going to create a "hit cache" for orders, so we can add the order into our list if we have at least one
    # line of the order with paid/fulfilled. Vs. just doing "last_order" back-reference, only incase we ever
    # encounter orders listed "out of order" and not back-to-back (shouldn't, but might as well be safe)
    order_cache = dict()
    input_contents = csv.reader(input_csv)

    # Skip the first line in the CSV, this will describe the CSV as a text header
    next(input_contents)

    for row in input_contents:

        skip_order = True
        # Only Migrate Paid and Fulfilled Orders, unfortunately Shopify only lists the first item in an order
        # as "paid" and "fulfilled", the rest are left empty.

        # "In your order CSV file, orders with multiple line items show their additional line items on separate lines.
        # Many of the fields are left blank to indicate that multiple items were purchased on the same order."
        # https://help.shopify.com/en/manual/orders/export-orders

        # So, the first time we encounter a good healthy order with paid/fulfilled we will put it into our
        # order hit table, and test it's existence in the case that paid/fulfilled is empty on a line item.

        # First, we need to remove the "#" from the front of orders, WooCommerce doesn't like it.
        order = row[fields.name].replace("#", "")
        financial_status = row[fields.financial_status]
        # This is a throw away field but we need to use it a few times so give it a name.
        fulfillment_status = row[fields.fulfillment_status]

        # Future thoughts: create a third CSV that contains all the orders we're skipping so they can be
        # reviewed to see if they are important or not.
        if financial_status == "paid" and fulfillment_status == "fulfilled":
            skip_order = False
        elif financial_status == "" and fulfillment_status == "" and order_cache.get(order):
            skip_order = False

        if not skip_order:
            # We will not accept all the fields of shopify, so we will skip things like "Fulfilled at"
            # and we won't need the "Fulfillment Status" either. Just financial status in that regard.
            cached_order = order_cache.get(order)

            # Absorb only the row entries we need, some will be empty because the order
            # is a secondary line item of a larger order, for those we'll draw from the
            # cache -- or, if no cache exists for the order, it's the first time encountering
            # the order, so we'll cache the required data (not all, just the stuff that will
            # be missing)
            email = row[fields.name]
            paid_at = row[fields.paid_at]
            currency = row[fields.currency]
            shipping_total = row[fields.shipping]
            order_total = row[fields.total]
            shipping_method = row[fields.shipping_method]
            created_at = row[fields.created_at]
            item_quantity = row[fields.lineitem_quantity]
            item_name = row[fields.lineitem_name]
            item_total = row[fields.lineitem_price]
            item_sku = row[fields.lineitem_sku]

            if cached_order:
                # The order wa found, so there will be some fields that are empty. We
                # won't even bother to check them, just used the cached information.
                billing_first_name = order_cache[order]["billing_first_name"]
                billing_last_name = order_cache[order]["billing_last_name"]
                billing_address1 = order_cache[order]["billing_address1"]
                billing_address2 = order_cache[order]["billing_address2"]
                billing_company = order_cache[order]["billing_company"]
                billing_city = order_cache[order]["billing_city"]
                billing_zip = order_cache[order]["billing_zip"]
                billing_state = order_cache[order]["billing_state"]
                billing_country = order_cache[order]["billing_country"]
                billing_phone = order_cache[order]["billing_phone"]

            else:
                # Not cached. We will by the end though.
                billing_address1 = row[fields.billing_address1]
                billing_address2 = row[fields.billing_address2]
                billing_company = row[fields.billing_company]
                billing_city = row[fields.billing_city]
                billing_zip = row[fields.billing_zip]
                billing_state = row[fields.billing_province]
                billing_country = row[fields.billing_country]
                billing_phone = row[fields.billing_phone]

                # Odd bug, the export for many of the zipcodes has a ' mark in them, clean it out.
                # This also appeared in the import into Google Sheets as well, must be a bug in shopify
                billing_zip = billing_zip.replace("'", "")

                billing_first_name, billing_last_name = split_name(row[fields.billing_name])

                # Add to our hit cache so we can absorb all further line items
                order_cache[order] = {
                    "billing_first_name": billing_first_name,
                    "billing_last_name": billing_last_name,
                    "billing_address1": billing_address1,
                    "billing_address2": billing_address2,
                    "billing_company": billing_company,
                    "billing_city": billing_city,
                    "billing_zip": billing_zip,
                    "billing_state": billing_state,
                    "billing_country": billing_country,
                    "billing_phone": billing_phone,

                }

            print(f"Order Number: {order}")
            print(f"E-mail Address: {email}")
            print(f"Billing First Name: {billing_first_name}")
            print(f"Billing Last Name: {billing_last_name}")
            print(f"Billing Addr1: {billing_address1}")
            print(f"Billing Addr2: {billing_address2}")
            print(f"Billing Company: {billing_company}")
            print(f"Billing City: {billing_city}")
            print(f"Billing Zip: {billing_zip}")
            print(f"Billing State: {billing_state}")
            print(f"Billing Country: {billing_country}")
            print(f"Billing Phone: {billing_phone}")

