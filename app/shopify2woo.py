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
    print(f"Your CVF is called {input_csv} to {output_csv}")
    input_contents = csv.reader(input_csv, delimiter=' ')
    for row in input_contents:
        print(', '.join(row))
