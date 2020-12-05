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
    "total_discount",
    "payment_method",
    "currency",
    "billing_first_name",
    "billing_last_name",
    "billing_email",
    "billing_phone",
    "billing_address_1",
    "billing_address_2",
    "billing_postcode",
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
@click.option("-u",
              "--sku-placeholder",
              "sku_placeholder",
              type=str,
              help="SKU name/id to use to fix missing SKU issues")
@click.option("-s",
              "--sample",
              "sample_size",
              type=int,
              help="Allow a smaller order sample size for dry-run imports.")
@click.option("-o",
              "--order",
              "order_export",
              type=str,
              help="Export a very specific order (good for testing).")
@click.option("-c",
              "--clean-only",
              "clean_only",
              help="Only write out orders that do not generate warnings on e-mail addresses, SKU's, etc.",
              is_flag=True)
@click.argument("input_csv",
                type=click.File('r'))
@click.argument("output_csv",
                type=click.File('w'))
def cli(input_csv, output_csv, sample_size, order_export, clean_only, sku_placeholder):
    """
    Convert INPUT_CSV file (e.g. order_export_1.csv) to OUTPUT_CSV (e.g. woocommerce_export.csv).

    All orders listed as "paid" and "fulfilled" will be imported, warnings will be displayed which may cause
    WooCommerce to fail to input the specific order.
    """
    # We will cache all incoming orders and write them out after they're all collected. While this isn't optimal
    # for large datasets, our test dataset was about 11k orders. Shopfiy creates a new "order entry" for every
    # item in an order; so we will need to combine them together into one single Order class (which is easier if we
    # cache the order).
    order_cache = dict()
    order_commits = 0

    # the two files are open by click.File() and closed when we leave scope, easy peasy.
    input_contents = csv.reader(input_csv)
    csv_writer = csv.writer(output_csv)

    # Skip the first line in the CSV, this will describe the CSV as a text header
    next(input_contents)

    if sample_size:
        print(f"Limiting output to sample size of {sample_size}")

    for row in input_contents:

        # Only Migrate Paid and Fulfilled Orders, unfortunately Shopify only lists the first item in an order
        # as "paid" and "fulfilled", the rest are left empty.

        # "In your order CSV file, orders with multiple line items show their additional line items on separate lines.
        # Many of the fields are left blank to indicate that multiple items were purchased on the same order."
        # https://help.shopify.com/en/manual/orders/export-orders

        # First, we need to remove the "#" from the front of orders, WooCommerce doesn't like it.
        order_number = row[fields.name].replace("#", "")

        financial_status = row[fields.financial_status]
        # This is a throw away field but we need to use it a few times so give it a name.
        fulfillment_status = row[fields.fulfillment_status]

        # Future thoughts: create a third CSV that contains all the orders we're skipping so they can be
        # reviewed to see if they are important or not.
        if (financial_status == "paid" and fulfillment_status == "fulfilled") or order_cache.get(order_number):

            # Get our cached order, if it isn't in the cache, it will return NONE and we will create a new order.
            cached_order = order_cache.get(order_number)

            if cached_order:
                # Hit! That means the order exists, this line is jus a new item entry for it.
                cached_order.add_item(row)
            else:
                # A new order, set up the base stuff and get it into our cache.
                order_commits = order_commits + 1
                cached_order = Order(row, sku_placeholder)

                # Cache it so we have it later.
                order_cache[order_number] = cached_order

            # If we exceed a sample size (if it's enabled) bail, we've got enough orders for our sample.
            if sample_size and order_commits >= sample_size:
                break

    # write our column header before jumping into our loop.
    csv_writer.writerow(woocommerce_columns)

    if order_export:
        if order_cache.get(order_export):
            total_errors = order_cache[order_export].error_list()

            for error in total_errors:
                print(error)

            if clean_only:
                if len(total_errors) == 0:
                    csv_writer.writerow(order_cache[order_export].build_record())
                    print(f"Exported 1 order (order number {order_export})")
                else:
                    print(f"Skipping order {order_export} due to warnings")
            else:
                csv_writer.writerow(order_cache[order_export].build_record())
                print(f"Exported 1 order (order number {order_export})")
        else:
            print(f"% Error: The order {order_export} was not found in your dataset")
    else:
        total_orders = 0
        for order in order_cache:

            total_errors = order_cache[order].error_list()

            for error in total_errors:
                print(error)

            if clean_only:
                if len(total_errors) == 0:
                    total_orders = total_orders + 1
                    csv_writer.writerow(order_cache[order].build_record())
                else:
                    print(f"Skipping order {order} due to warnings")
            else:
                total_orders = total_orders + 1
                csv_writer.writerow(order_cache[order].build_record())

        print(f"Exported {total_orders} orders(s)")
