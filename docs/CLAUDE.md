# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**3 Delta Dental** is a B2B e-commerce Shopify store for professional dental lab supplies and equipment. It uses the **Shopify Horizon theme (v3.2.1)** with extensive customizations.

**Key Design Principle:** The site is built for busy dental professionals who need to find and purchase products quickly. Search-first design with prominent SKU/product code matching is essential.

## Tech Stack

- **Theme Framework:** Shopify Horizon (v3.2.1)
- **Templating:** Liquid (.liquid/.json files)
- **Styling:** CSS (in assets/)
- **Scripts:** JavaScript (in assets/)
- **Automation:** Python 3 (for product management via Shopify Admin API)
- **API:** Shopify Admin API (GraphQL, v2024-10)
- **Deployment:** Shopify CLI

## Deployment & Development

### Push Theme Changes to Shopify
```bash
shopify theme push --store=3-delta-dental.myshopify.com --theme=153395462296
```

### Development Mode (Auto-Sync)
```bash
shopify theme dev --store=3-delta-dental.myshopify.com --theme=153395462296
```
Recommended during active development - automatically syncs file changes in real-time.

### Product Management
Python script at `shopify_product_management.py` handles:
- Drafting products with no images
- Enabling inventory tracking for variants
- Uses Shopify Admin API with GraphQL

To run with authentication:
```bash
python3 shopify_product_management.py
```

## Directory Structure

```
/sections/         - Reusable template sections (Liquid files)
/blocks/           - Block components for sections
/templates/        - Page templates (JSON files reference sections)
/snippets/         - Reusable Liquid code fragments
/layout/           - Main layout files (theme.liquid, password.liquid)
/assets/           - CSS, JS, images, logos
/config/           - Theme settings (settings_schema.json, settings_data.json)
/locales/          - Translation files
```

## Key Custom Sections

These custom sections have been created for the 3 Delta Dental site:

- **about-page.liquid** - About Us page with company history
- **brands-page.liquid** - Brand showcase/landing
- **brand-showcase.liquid** - Brand logo grid component
- **cart-po-field.liquid** - Purchase order number field for B2B orders
- **clearance-page.liquid** - Clearance products section
- **contact-page.liquid** - Contact information and form
- **custom-404.liquid** - Custom 404 error page
- **new-products-page.liquid** - New arrivals showcase
- **policy-page.liquid** - General policy/legal content template
- **product-tga-specs.liquid** - TGA compliance specifications for products
- **trade-account-page.liquid** - Trade account information

## Important Pages & Templates

| Page | Template | Purpose |
|------|----------|---------|
| Homepage | index.json | Hero search + category grid + featured products |
| About | page.about.json | Company info, TGA approval, distributor status |
| Contact | page.contact-custom.json | Contact form + business hours + address |
| Brands | page.brands.json | Brand showcase and navigation |
| Product | product.json | SKU display, GST pricing, related products |
| Cart | cart.json | Cart with PO field for B2B |
| Search | search.json | Search results |
| Clearance | page.clearance.json | Clearance items |
| FAQ | page.faq.json | Frequently asked questions |
| New Products | page.new-products.json | New arrivals |
| Returns | page.returns.json | Returns policy |
| Shipping | page.shipping.json | Shipping info & delivery times |
| Terms | page.terms.json | Terms and conditions |
| Privacy | page.privacy.json | Privacy policy |

## Brand & Design System

### Colors
- **Primary Green:** `#03B239` (Buttons, CTAs, Success states)
- **Dark Blue:** `#003B56` (Headers, Trust elements)
- **Gold Accent:** `#FED440` (Highlights, Special offers)
- **Light Gray:** `#F7F7F7` (Secondary backgrounds, cards)
- **Dark Gray:** `#0D0D0D` (Body text)

### Typography
- **Headings:** Oswald (Bold, Uppercase for major headings)
- **Body:** System fonts (Helvetica, Arial, sans-serif)

### Business Context
- **Pricing:** All prices displayed **exclusive of GST** (B2B model)
- **Company Details:**
  - ABN: 67 354 783 242
  - Address: 1/5a Ashton Street, Labrador, QLD 4215
  - Email: info@3deltadental.com
  - Sales: +61 448 419 050 (Emilio Ragazzo)
  - Tech Support: +61 478 731 344
  - Business hours: Monday-Friday, specific times in pages

## Critical Features for B2B Context

1. **SKU Search** - Search must support product codes/SKUs prominently
2. **Stock Indicators** - Clear in-stock/low-stock/out-of-stock status
3. **GST Exclusion** - Display "excl. GST" on all pricing
4. **PO Numbers** - Cart includes PO field for bulk orders
5. **Professional Tone** - No marketing fluff, direct and technical
6. **Brand Registry** - Brand pages and filtering for professional reorders

## Liquid & JSON Structure

### Section Files (.liquid)
Sections use Liquid schema blocks to define settings editable in Shopify Admin:
```liquid
{% schema %}
{
  "name": "Section Name",
  "settings": [{...}],
  "blocks": [{...}]
}
{% endschema %}
```

### Template Files (.json)
Templates define page sections as JSON arrays:
```json
{
  "sections": {
    "section_id": {
      "type": "section-name",
      "settings": {...}
    }
  },
  "order": ["section_id"]
}
```

## Common Customization Points

### Adding New Section
1. Create file in `/sections/`
2. Define schema with Liquid `{% schema %}` block
3. Reference in template JSON files
4. Settings auto-editable via Shopify Admin theme editor

### Modifying Product Pages
Edit `/templates/product.json` to:
- Add/remove sections
- Modify featured product section
- Adjust related products display
- Ensure SKU and GST pricing remain visible

### Updating Brand Colors
Edit color values in `/config/settings_schema.json` and they automatically propagate through the theme.

## Product Import/Export

- **CSV Format:** `shopify_products_import.csv`
- **Import Method:** Shopify Admin → Products → Import
- **Automated Processing:** Python script handles image detection and inventory tracking

## Testing Checklist

Before pushing changes:
- [ ] All pages load in < 3 seconds
- [ ] Search works (test with product codes/SKUs)
- [ ] Mobile experience is smooth (breakpoints: <768px mobile, 768-1024px tablet, >1024px desktop)
- [ ] Product images are optimized
- [ ] Cart PO field displays correctly
- [ ] GST "excl. GST" text appears on all pricing
- [ ] Brand colors consistent throughout
- [ ] All links in footer/nav working
- [ ] Contact information visible and accurate

## Resources

- **Shopify Liquid Docs:** https://shopify.dev/docs/api/liquid
- **Horizon Theme Docs:** https://help.shopify.com/manual/online-store/themes
- **Shopify CLI:** https://shopify.dev/docs/themes/tools/cli
- **Admin API GraphQL:** https://shopify.dev/docs/api/admin-rest

## Recent Work

Latest commits involved:
- Adding hero banner and completing new pages (FAQ, Brands, Trade Account, TGA Compliance)
- Converting WordPress content to Shopify Liquid format
- Product management automation with Python
- Brand logo uploads and configuration

See `BUILD_COMPLETE.md`, `CONVERSION_COMPLETE.md`, and `SITEMAP_AND_DESIGN_STRATEGY.md` for detailed project history.
