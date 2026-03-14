# 3 Delta Dental - Shopify Theme

B2B e-commerce store for professional dental lab supplies and equipment. Built on Shopify Horizon theme with extensive customizations.

## Project Organization

### Directory Structure

```
/sections/         - Reusable Liquid template sections
/blocks/           - Block components for sections
/templates/        - Page templates (JSON format)
/snippets/         - Reusable Liquid code fragments
/layout/           - Main layout files
/assets/           - CSS, JavaScript, images, logos
/config/           - Theme settings schema
/locales/          - Translation files
/docs/             - Project documentation
/automation/       - Python automation scripts
/exports/          - Generated files (not version controlled)
/brand-logos/      - Brand logo assets
```

## Documentation (/docs/)

- **CLAUDE.md** - Instructions for Claude Code instances
- **DESIGN_STRATEGY.md** - UX/UI design principles and brand guidelines
- **BUILD_COMPLETE.md** - Build summary and customizations
- **CONVERSION_COMPLETE.md** - WordPress to Shopify migration docs
- **DEPLOYMENT_INSTRUCTIONS.md** - Deployment procedures
- Additional reference files

## Automation Scripts (/automation/)

### shopify_product_management.py
Manages products via Shopify Admin API:
- Drafts products with no images
- Enables inventory tracking
- Uses GraphQL API (v2024-10)

**Usage:**
```bash
python3 automation/shopify_product_management.py
```

### woocommerce_to_shopify_converter.py
Converts products from WooCommerce to Shopify format.

**Authentication:**
Set environment variables:
- `SHOPIFY_ACCESS_TOKEN`
- `SHOPIFY_SHOP_NAME`

## Generated Files (/exports/)

Automatically created by automation scripts (added to `.gitignore`):
- `drafted_products*.csv` - Draft product listings
- `inventory_updates*.csv` - Inventory sync data
- `product_management_summary*.json` - Automation summaries
- `shopify_products_import.csv` - Shopify import file

## Development

### Push Theme Changes
```bash
shopify theme push --store=3-delta-dental.myshopify.com --theme=153395462296
```

### Development Mode (Auto-Sync)
```bash
shopify theme dev --store=3-delta-dental.myshopify.com --theme=153395462296
```

## Key Features

- **B2B Focus** - All prices displayed exclusive of GST
- **SKU Search** - Product code matching
- **Stock Indicators** - In-stock/low-stock status
- **PO Field** - Purchase order numbers for bulk orders
- **Professional Tone** - Direct, technical content
- **Brand Registry** - Brand pages and filtering

## Brand Reference

**Colors:**
- Primary Green: `#03B239` (CTAs, buttons)
- Dark Blue: `#003B56` (Headers, trust elements)
- Gold Accent: `#FED440` (Highlights)

**Typography:**
- Headings: Oswald
- Body: System fonts

**Company Details:**
- ABN: 67 354 783 242
- Email: info@3deltadental.com
- Address: 1/5a Ashton Street, Labrador, QLD 4215
