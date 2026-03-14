# Automation Scripts

This directory contains Python scripts for automating product management and theme migration tasks.

## Scripts

### shopify_product_management.py
Manages products in Shopify via the Admin API:
- Drafts products with no images
- Enables inventory tracking for variants
- Syncs product data
- Uses GraphQL API (v2024-10)

**Usage:**
```bash
python3 shopify_product_management.py
```

### woocommerce_to_shopify_converter.py
Automated conversion tool for migrating products from WooCommerce to Shopify format.

## Authentication

Scripts use Shopify Admin API credentials. Ensure environment variables are configured:
- `SHOPIFY_ACCESS_TOKEN`
- `SHOPIFY_SHOP_NAME`
