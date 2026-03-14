#!/usr/bin/env python3
"""
WooCommerce to Shopify Product CSV Converter
Converts WooCommerce product export to Shopify product import format
"""

import csv
import re
from html import unescape
from typing import List, Dict, Any

def create_handle(name: str) -> str:
    """Create a Shopify-friendly handle from product name"""
    handle = name.lower()
    handle = re.sub(r'[^\w\s-]', '', handle)
    handle = re.sub(r'[-\s]+', '-', handle)
    return handle.strip('-')

def clean_html(html: str) -> str:
    """Clean and unescape HTML content"""
    if not html:
        return ""
    # Unescape HTML entities
    cleaned = unescape(html)
    # Replace literal \n with actual newlines first
    cleaned = cleaned.replace('\\n', '\n')

    # Split into paragraphs (double line breaks)
    paragraphs = re.split(r'\n\s*\n', cleaned)

    # Wrap each paragraph in <p> tags and convert single line breaks to <br>
    formatted_paragraphs = []
    for para in paragraphs:
        if para.strip():
            # Convert single line breaks within paragraph to <br>
            para = para.replace('\n', '<br>')
            # Wrap in paragraph tag
            formatted_paragraphs.append(f"<p>{para.strip()}</p>")

    return '\n'.join(formatted_paragraphs)

def kg_to_grams(kg_str: str) -> str:
    """Convert kg to grams"""
    try:
        kg = float(kg_str) if kg_str else 0
        return str(int(kg * 1000))
    except:
        return "0"

def parse_categories(categories: str) -> tuple:
    """Parse WooCommerce categories into Shopify Product Category and Type"""
    if not categories:
        return ("", "")

    cats = [c.strip() for c in categories.split(',')]
    # Leave Product Category blank (Shopify uses standardized taxonomy)
    # Use all categories in Type field for B2B flexibility
    product_category = ""  # Leave blank to avoid taxonomy errors
    product_type = ", ".join(cats) if cats else ""

    return (product_category, product_type)

def parse_images(images_str: str) -> List[str]:
    """Parse comma-separated image URLs"""
    if not images_str:
        return []
    return [img.strip() for img in images_str.split(',') if img.strip()]

def convert_woocommerce_to_shopify(input_file: str, output_file: str):
    """Main conversion function"""

    with open(input_file, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        wc_products = list(reader)

    # Shopify CSV structure
    shopify_headers = [
        'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type',
        'Tags', 'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name',
        'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU',
        'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty',
        'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price',
        'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable',
        'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text',
        'Gift Card', 'SEO Title', 'SEO Description', 'Variant Image',
        'Variant Weight Unit', 'Variant Tax Code', 'Cost per item', 'Status'
    ]

    shopify_products = []

    for wc_product in wc_products:
        # Skip if no name
        if not wc_product.get('Name'):
            continue

        handle = create_handle(wc_product['Name'])
        title = wc_product['Name']
        body_html = clean_html(wc_product.get('Description', ''))
        short_desc = clean_html(wc_product.get('Short description', ''))

        # Combine short and full description
        if short_desc and body_html:
            body_html = f"{short_desc}\n{body_html}"
        elif short_desc:
            body_html = short_desc

        vendor = wc_product.get('Brand', '') or wc_product.get('Brands', '')
        product_category, product_type = parse_categories(wc_product.get('Categories', ''))
        tags = wc_product.get('Tags', '')

        # Price handling
        regular_price = wc_product.get('Regular price', '0')
        sale_price = wc_product.get('Sale price', '')
        variant_price = sale_price if sale_price else regular_price
        compare_at_price = regular_price if sale_price else ''

        # Stock
        in_stock = wc_product.get('In stock?', '0')
        stock_qty = wc_product.get('Stock', '0')

        # Weight
        weight_kg = wc_product.get('Weight (kg)', '0')
        weight_grams = kg_to_grams(weight_kg)

        # SKU
        sku = wc_product.get('SKU', '')

        # Images
        images = parse_images(wc_product.get('Images', ''))

        # Check if product has variants (attributes)
        has_variants = False
        variants_data = []

        # Check for attributes
        attr1_name = wc_product.get('Attribute 1 name', '')
        attr1_values = wc_product.get('Attribute 1 value(s)', '')
        attr2_name = wc_product.get('Attribute 2 name', '')
        attr2_values = wc_product.get('Attribute 2 value(s)', '')

        if attr1_name and attr1_values:
            has_variants = True
            values1 = [v.strip() for v in attr1_values.split(',')]

            if attr2_name and attr2_values:
                values2 = [v.strip() for v in attr2_values.split(',')]
                # Create combinations
                for v1 in values1:
                    for v2 in values2:
                        variants_data.append({
                            'option1_name': attr1_name,
                            'option1_value': v1,
                            'option2_name': attr2_name,
                            'option2_value': v2
                        })
            else:
                for v1 in values1:
                    variants_data.append({
                        'option1_name': attr1_name,
                        'option1_value': v1,
                        'option2_name': '',
                        'option2_value': ''
                    })

        # Create Shopify rows
        if has_variants and variants_data:
            # First row with product info
            for idx, variant in enumerate(variants_data):
                row = {
                    'Handle': handle,
                    'Title': title if idx == 0 else '',
                    'Body (HTML)': body_html if idx == 0 else '',
                    'Vendor': vendor if idx == 0 else '',
                    'Product Category': product_category if idx == 0 else '',
                    'Type': product_type if idx == 0 else '',
                    'Tags': tags if idx == 0 else '',
                    'Published': 'TRUE',
                    'Option1 Name': variant['option1_name'],
                    'Option1 Value': variant['option1_value'],
                    'Option2 Name': variant.get('option2_name', ''),
                    'Option2 Value': variant.get('option2_value', ''),
                    'Option3 Name': '',
                    'Option3 Value': '',
                    'Variant SKU': f"{sku}-{variant['option1_value']}" if sku else '',
                    'Variant Grams': weight_grams,
                    'Variant Inventory Tracker': 'shopify',
                    'Variant Inventory Qty': stock_qty,
                    'Variant Inventory Policy': 'deny',
                    'Variant Fulfillment Service': 'manual',
                    'Variant Price': variant_price,
                    'Variant Compare At Price': compare_at_price,
                    'Variant Requires Shipping': 'TRUE',
                    'Variant Taxable': 'TRUE',
                    'Variant Barcode': '',
                    'Image Src': '',
                    'Image Position': '',
                    'Image Alt Text': '',
                    'Gift Card': 'FALSE',
                    'SEO Title': title if idx == 0 else '',
                    'SEO Description': short_desc if idx == 0 else '',
                    'Variant Image': '',
                    'Variant Weight Unit': 'g',
                    'Variant Tax Code': '',
                    'Cost per item': '',
                    'Status': 'active'
                }
                shopify_products.append(row)

            # Add image rows
            for img_idx, img_url in enumerate(images):
                img_row = {header: '' for header in shopify_headers}
                img_row['Handle'] = handle
                img_row['Image Src'] = img_url
                img_row['Image Position'] = str(img_idx + 1)
                img_row['Image Alt Text'] = title
                shopify_products.append(img_row)
        else:
            # Simple product without variants
            row = {
                'Handle': handle,
                'Title': title,
                'Body (HTML)': body_html,
                'Vendor': vendor,
                'Product Category': product_category,
                'Type': product_type,
                'Tags': tags,
                'Published': 'TRUE',
                'Option1 Name': 'Title',
                'Option1 Value': 'Default Title',
                'Option2 Name': '',
                'Option2 Value': '',
                'Option3 Name': '',
                'Option3 Value': '',
                'Variant SKU': sku,
                'Variant Grams': weight_grams,
                'Variant Inventory Tracker': 'shopify',
                'Variant Inventory Qty': stock_qty,
                'Variant Inventory Policy': 'deny',
                'Variant Fulfillment Service': 'manual',
                'Variant Price': variant_price,
                'Variant Compare At Price': compare_at_price,
                'Variant Requires Shipping': 'TRUE',
                'Variant Taxable': 'TRUE',
                'Variant Barcode': '',
                'Image Src': images[0] if images else '',
                'Image Position': '1' if images else '',
                'Image Alt Text': title if images else '',
                'Gift Card': 'FALSE',
                'SEO Title': title,
                'SEO Description': short_desc,
                'Variant Image': '',
                'Variant Weight Unit': 'g',
                'Variant Tax Code': '',
                'Cost per item': '',
                'Status': 'active'
            }
            shopify_products.append(row)

            # Add additional images
            for img_idx, img_url in enumerate(images[1:], start=2):
                img_row = {header: '' for header in shopify_headers}
                img_row['Handle'] = handle
                img_row['Image Src'] = img_url
                img_row['Image Position'] = str(img_idx)
                img_row['Image Alt Text'] = title
                shopify_products.append(img_row)

    # Write to output file
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=shopify_headers)
        writer.writeheader()
        writer.writerows(shopify_products)

    print(f"✓ Conversion complete!")
    print(f"  Input: {len(wc_products)} WooCommerce products")
    print(f"  Output: {output_file}")
    print(f"  Total rows: {len(shopify_products)} (including variants and images)")

if __name__ == "__main__":
    input_file = "/Users/bfjdigital7/Downloads/wc-product-export-28-1-2026-1769607203074.csv"
    output_file = "/Users/bfjdigital7/Documents/3DeltaDental/shopify_products_import.csv"

    convert_woocommerce_to_shopify(input_file, output_file)
