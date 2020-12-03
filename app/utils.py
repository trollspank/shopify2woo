"""utils
We will collect a list of all utility functions that make parsing our CSV and exporting
the correct data a bit easier. Rather than clogging up the main CLI routines with these
functions, we'll store them here.
"""


def split_name(name):
    """
    Split a long form name like "Derrick J Schommer" into "Derrick" and "J Schommer".

    The Shopify system uses one long name field, where WooCommerce uses 2 fields for
    first and last name (and we'll just stuff all the extra letters into the second field
    if they have middle initials, or are a Jr. or III, etc.)

    Parameters
    ----------
    name: The name of the customer like "Derrick Schommer" or "Derrick J Schommer III"

    Returns
    -------
    str, str : returns two strings, the first name and the rest (as last name)
    """
    first_name = ""
    last_name = ""

    # Split name by spaces as most humans do (at least many languages)
    name_array = name.split(" ")
    first_name = name_array[0]

    if len(name_array) > 1:
        # Oh yay, seems the customer has a last name :-)
        name_array.pop(0)  # kick the first name out.
        last_name = ' '.join([str(elem) for elem in name_array])

    return (first_name, last_name)

