"""fields
The CSV module uses element offsets for everything, we're just going to fix those
elements to field names so it's easier to understand what we are working with and
if we mess one up, we can change the constant.

These fields map to those found in ../docs/shopify_columns.txt
"""


name=0
email=1
financial_status = 2
paid_at = 3
fulfillment_status = 4
fulfilled_at = 5
accepts_marketing = 6
currency = 7
subtotal = 8
shipping = 9
taxes = 10
total = 11
discount_code = 12
discount_amount = 13
shipping_method = 14
created_at = 15
lineitem_quantity = 16
lineitem_name = 17
lineitem_price = 18
lineitem_compare_at = 19
lineitem_sku = 20
lineitem_requires_shipping = 21
lineitem_taxable = 22
lineitem_fulfillment_status = 23
billing_name = 24
billing_street = 25
billing_address1 = 26
billing_address2 = 27
billing_company = 28
billing_city = 29
billing_zip = 30
billing_province = 31
billing_country = 32
billing_phone = 33
shipping_name = 34
shipping_street = 35
shipping_address1 = 36
shipping_address2 = 37
shipping_company = 38
shipping_city = 39
shipping_zip = 40
shipping_province = 41
shipping_country = 42
shipping_phone = 43
notes = 44
# Skipping a bunch of unused fields (in WooCommerce so no need to address them)
payment_method = 47
tax_1_value = 61
