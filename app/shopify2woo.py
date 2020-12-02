import click


@click.command()
@click.option("-o",
              "--outputCSV",
              "output_csv",
              type=str,
              default="woo_orders.csv",
              help="The .csv file which can be used to import into WooCommerce (default: woo_orders.csv)")
@click.argument('csvfile')
def cli(csvfile):
    print("Your CVF is called {csvfile}")
