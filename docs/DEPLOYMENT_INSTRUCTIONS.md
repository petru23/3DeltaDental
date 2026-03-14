# Deployment Instructions

## To Push Theme Changes to Shopify

Run this command in your terminal (it requires interactive confirmation):

```bash
cd /Users/bfjdigital7/Documents/3DeltaDental
shopify theme push --store=3-delta-dental.myshopify.com --theme=153395462296
```

When prompted, confirm "Yes" to push the changes to your live theme.

## OR Use Development Mode (Recommended During Build)

For automatic syncing while building:

```bash
shopify theme dev --store=3-delta-dental.myshopify.com --theme=153395462296
```

This will:
- Start a local preview server
- Automatically sync any file changes to Shopify
- Allow you to see changes in real-time

## Import Products

The products CSV is ready at: `shopify_products_import.csv`

To import:
1. Go to: https://3-delta-dental.myshopify.com/admin/products
2. Click "Import"
3. Upload `shopify_products_import.csv`
4. Map columns (should auto-map)
5. Click "Import products"

---

## What's Been Done So Far

✓ Brand colors applied (Green #03B239, Blue #003B56, Gold #FED440)
✓ Color schemes configured for theme editor
✓ Logo files downloaded
✓ 699 products converted to Shopify format
✓ Theme structure analyzed and ready for customization
