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
    order_table = dict()
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
        order = row[0].replace("#", "")
        financial_status = row[2]

        # This is a throw away field but we need to use it a few times so give it a name.
        fulfillment_status = row[4]

        # Future thoughts: create a third CSV that contains all the orders we're skipping so they can be
        # reviewed to see if they are important or not.
        if financial_status == "paid" and fulfillment_status == "fulfilled":
            skip_order = False
        elif financial_status == "" and fulfillment_status == "" and order_table.get(order):
            skip_order = False

        if not skip_order:
            # We will not accept all the fields of shopify, so we will skip things like "Fulfilled at"
            # and we won't need the "Fulfillment Status" either. Just financial status in that regard.

            # Absorb only the row entries we need:
            email = row[1]
            paid_at = row[3]
            currency = row[7]
            shipping_total = row[9]
            order_total = row[11]
            shipping_method = row[14]
            created_at = row[15]
            item_quantity = row[16]
            item_name = row[17]
            item_total = row[18]
            item_sku = row[20]

            if row[24] == "":
                # The name wasn't included in the line item, we'll have to pull from the cache
                billing_first_name = order_table[order]['billing_first_name']
                billing_last_name = order_table[order]['billing_last_name']
            else:
                # Billing name will be split into a first,second names where Shopify used
                # one long name. We will take any middle names or other "things" in the name
                # (e.g. "Jr, III, etc.") and just stick them on the last name.
                name_array = row[24].split(" ")
                billing_first_name = name_array[0]

                if len(name_array) > 1:
                    # Oh yay, seems the customer has a last name :-)
                    name_array.pop(0)  # kick the first name out.
                    billing_last_name = ' '.join([str(elem) for elem in name_array])
                else:
                    billing_last_name = ""  # Trust me, some folks don't use/have last name.

                # Add to our hit cache so we can absorb all further line items
                order_table[order] = {
                    "billing_first_name": billing_first_name,
                    "billing_last_name": billing_last_name,
                }

            print(f"Order Number: {order}")
            print(f"E-mail Address: {email}")
            print(f"Billing First Name: {billing_first_name}")
            print(f"Billing Last Name: {billing_last_name}")
