"""Shopify2Woo
The objective of Shopify2Woo is to read in a Shopify order export CSV file (exported in Excel dialect)
and convert it into a file appropriate for importing into WooCommerce using the Import Orders CVS addon.

The guidance for the CSV import manipulation is based on the instructions on Importing orders written here:
https://docs.woocommerce.com/document/customer-order-csv-import-suite/

Unfortunately WooCommerce does not come with the ability to import orders and customers "out of the box"
without spending more money.
"""

# Required Imports
import click
import csv

# My custom imports
import fields
from order import Order
from utils import split_name

# The WooCommerce fields (in order) we'll use to write to for the header of the CSV output for WooCommerce
woocommerce_columns = [
    "order_number",
    "created_at",
    "status",
    "total",
    "total_shipping",
    "cart_tax",
    "shipping_tax",
    "total_discount",
    "payment_method",
    "currency",
    "billing_first_name",
    "billing_last_name",
    "billing_email",
    "billing_phone",
    "billing_address_1",
    "billing_address_2",
    "bil,ling_postcode"
    "billing_city",
    "billing_state",
    "billing_country",
    "billing_company",
    "shipping_first_name",
    "shipping_last_name",
    "shipping_address_1",
    "shipping_address_2",
    "shipping_postcode",
    "shipping_city",
    "shipping_state",
    "shipping_country",
    "shipping_company",
    "note",
    "line_items",
    "shipping_lines",
]


@click.command()
@click.option("-s", "--sample", 'sample_size', type=int, help="Allow a smaller order sample size for dry-run imports.")
@click.argument("input_csv", type=click.File('r'))
@click.argument("output_csv", type=click.File('w'))
def cli(input_csv, output_csv, sample_size):
    """
    Entry point for executing the base functionality for shopify2woo, this sucker will take the CSV file
    of data from Shopify and burp out an output CSV that can be imported into WooCommerce.

    Parameters
    ----------
    input_csv: the csv file from Shopify
    output_csv: the new csv file for WooCommerce
    sample_size: How many full orders to export (to sample the data)
    Returns
    -------

    """
    # Going to create a "hit cache" for orders, so we can add the order into our list if we have at least one
    # line of the order with paid/fulfilled. Vs. just doing "last_order" back-reference, only incase we ever
    # encounter orders listed "out of order" and not back-to-back (shouldn't, but might as well be safe)
    order_cache = dict()
    order_commits = 0
    last_order = None

    input_contents = csv.reader(input_csv)
    csv_writer = csv.writer(output_csv)
    # Skip the first line in the CSV, this will describe the CSV as a text header
    next(input_contents)

    if sample_size:
        print(f"Limiting output to sample size of {sample_size}")

    csv_writer.writerow(woocommerce_columns)

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
        order_number = row[fields.name].replace("#", "")

        financial_status = row[fields.financial_status]
        # This is a throw away field but we need to use it a few times so give it a name.
        fulfillment_status = row[fields.fulfillment_status]

        # Future thoughts: create a third CSV that contains all the orders we're skipping so they can be
        # reviewed to see if they are important or not.
        if financial_status == "paid" and fulfillment_status == "fulfilled":
            skip_order = False
        elif order_cache.get(order_number):
            skip_order = False

        if not skip_order:

            cached_order = order_cache.get(order_number)

            if cached_order:
                cached_order.add_item(row)
            else:
                order_commits = order_commits + 1
                cached_order = Order(row)
                # Cache it so we have it later.
                order_cache[order_number] = cached_order

            cached_order.dump()
            if sample_size and order_commits >= sample_size:
                break
