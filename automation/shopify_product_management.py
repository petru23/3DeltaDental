#!/usr/bin/env python3
"""
Shopify Product Management Script for 3 Delta Dental
Tasks:
1. Draft all products with no images
2. Enable inventory tracking for all product variants
"""

import json
import time
import csv
import sys
import ssl
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Configuration
STORE = "3-delta-dental.myshopify.com"
API_VERSION = "2024-10"
ACCESS_TOKEN = "atkn_2.CvYBCiQ3Y2MxMTAzYy1hN2MyLTQ1NDAtYjNmYi0wMjU2Y2U4NTljN2ESJDQwYTQ2NWI4LWE5N2ItNDViZS05ODllLTc2ZDVlOTlhNDkzNhoEAQMEDSCF_vXMBijAtvbMBjIkZjg5YjRhMDAtNWUzYS00YmY3LTlkZTctOTI2YTBlYzY5NWNlOiRmYmRiMjY0OS1lMzI3LTQ5MDctOGY2Ny05MDhkMjRjZmQ3ZTNCJDAxZjY0ZmFkLWQ0MGMtNGEyZC05YTM5LTdlNjdlODViYzJjYkokMjE0MzUwY2MtMWQwNC00MzQwLTkzOTItNzZlNmMwZmIyM2E1Em8KQDez-gY4M12-NWrdaCamkscW3VnizhLxQ102A06BfWxoQ5Tl9r6App692lxssgxgb1PUKtMRmkKv-0i3HZMOGA4SK0pJVFhpYk8wYzFUYWl2YXB0UHlIaUVaSDRzeENZZmpqNnc3ZW5keVN3UE0"

GRAPHQL_URL = f"https://{STORE}/admin/api/{API_VERSION}/graphql.json"

# SSL context - use unverified for macOS cert issues
SSL_CONTEXT = ssl._create_unverified_context()

# Track changes
drafted_products = []  # Products set to DRAFT
inventory_updates = []  # Variants with inventory tracking enabled
errors = []


def graphql_request(query, variables=None):
    """Make a GraphQL request to the Shopify Admin API."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    data = json.dumps(payload).encode("utf-8")
    req = Request(
        GRAPHQL_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result
    except HTTPError as e:
        error_msg = f"HTTP Error {e.code}: {e.reason}"
        print(f"  ERROR: {error_msg}")
        errors.append(error_msg)
        return None
    except URLError as e:
        error_msg = f"URL Error: {e.reason}"
        print(f"  ERROR: {error_msg}")
        errors.append(error_msg)
        return None


def fetch_all_products():
    """Fetch all products with their images and variants."""
    print("\n=== FETCHING ALL PRODUCTS ===")
    all_products = []
    cursor = None
    page = 0

    query = """
    query GetProducts($cursor: String) {
      products(first: 250, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          title
          status
          images(first: 1) {
            nodes {
              id
            }
          }
          variants(first: 100) {
            nodes {
              id
              title
              inventoryQuantity
              inventoryItem {
                id
                tracked
              }
            }
          }
        }
      }
    }
    """

    while True:
        page += 1
        print(f"  Fetching page {page}...")
        variables = {"cursor": cursor} if cursor else {}
        result = graphql_request(query, variables)

        if not result or "errors" in result:
            error_msg = f"GraphQL error on page {page}: {result}"
            print(f"  ERROR: {error_msg}")
            errors.append(error_msg)
            break

        products_data = result["data"]["products"]
        nodes = products_data["nodes"]
        all_products.extend(nodes)
        print(f"  Page {page}: {len(nodes)} products fetched (total: {len(all_products)})")

        if not products_data["pageInfo"]["hasNextPage"]:
            break

        cursor = products_data["pageInfo"]["endCursor"]
        time.sleep(0.3)  # Rate limiting

    print(f"\n  Total products fetched: {len(all_products)}")
    return all_products


def draft_product(product_id, product_title):
    """Set a product to DRAFT status."""
    mutation = """
    mutation UpdateProductStatus($id: ID!, $status: ProductStatus!) {
      productUpdate(product: {id: $id, status: $status}) {
        product {
          id
          title
          status
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {"id": product_id, "status": "DRAFT"}
    result = graphql_request(mutation, variables)

    if not result:
        return False

    if "errors" in result:
        error_msg = f"GraphQL error drafting {product_id}: {result['errors']}"
        print(f"    ERROR: {error_msg}")
        errors.append(error_msg)
        return False

    update_result = result.get("data", {}).get("productUpdate", {})
    user_errors = update_result.get("userErrors", [])

    if user_errors:
        error_msg = f"User errors drafting {product_title}: {user_errors}"
        print(f"    ERROR: {error_msg}")
        errors.append(error_msg)
        return False

    updated_product = update_result.get("product", {})
    if updated_product.get("status") == "DRAFT":
        return True

    return False


def enable_inventory_tracking(inventory_item_id, product_title, variant_title):
    """Enable inventory tracking for an inventory item."""
    mutation = """
    mutation EnableInventoryTracking($id: ID!) {
      inventoryItemUpdate(id: $id, input: {tracked: true}) {
        inventoryItem {
          id
          tracked
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {"id": inventory_item_id}
    result = graphql_request(mutation, variables)

    if not result:
        return False

    if "errors" in result:
        error_msg = f"GraphQL error enabling tracking for {inventory_item_id}: {result['errors']}"
        print(f"    ERROR: {error_msg}")
        errors.append(error_msg)
        return False

    update_result = result.get("data", {}).get("inventoryItemUpdate", {})
    user_errors = update_result.get("userErrors", [])

    if user_errors:
        error_msg = f"User errors enabling tracking for {product_title}/{variant_title}: {user_errors}"
        print(f"    ERROR: {error_msg}")
        errors.append(error_msg)
        return False

    item = update_result.get("inventoryItem", {})
    return item.get("tracked", False)


def process_no_image_products(all_products):
    """Draft all products that have no images."""
    print("\n=== TASK 1: DRAFTING PRODUCTS WITH NO IMAGES ===")

    no_image_products = [
        p for p in all_products if len(p["images"]["nodes"]) == 0
    ]

    print(f"\n  Found {len(no_image_products)} products with no images")
    print(f"  Total products: {len(all_products)}")

    already_draft = [p for p in no_image_products if p["status"] == "DRAFT"]
    need_to_draft = [p for p in no_image_products if p["status"] != "DRAFT"]

    print(f"  Already DRAFT: {len(already_draft)}")
    print(f"  Need to set to DRAFT: {len(need_to_draft)}")

    success_count = 0
    fail_count = 0

    for i, product in enumerate(need_to_draft, 1):
        product_id = product["id"]
        product_title = product["title"]
        current_status = product["status"]

        print(f"  [{i}/{len(need_to_draft)}] Drafting: {product_title[:60]}...")
        success = draft_product(product_id, product_title)

        if success:
            success_count += 1
            print(f"    OK - Set to DRAFT (was: {current_status})")
            drafted_products.append({
                "product_id": product_id,
                "title": product_title,
                "previous_status": current_status,
                "new_status": "DRAFT",
                "reason": "no_images",
            })
        else:
            fail_count += 1
            print(f"    FAILED - Could not draft product")

        time.sleep(0.2)  # Rate limiting

    print(f"\n  TASK 1 SUMMARY:")
    print(f"    Products with no images: {len(no_image_products)}")
    print(f"    Already DRAFT (unchanged): {len(already_draft)}")
    print(f"    Successfully set to DRAFT: {success_count}")
    print(f"    Failed to draft: {fail_count}")

    # Also track products that were already draft with no images
    for product in already_draft:
        drafted_products.append({
            "product_id": product["id"],
            "title": product["title"],
            "previous_status": "DRAFT",
            "new_status": "DRAFT",
            "reason": "no_images_already_draft",
        })

    return no_image_products


def process_inventory_tracking(all_products):
    """Enable inventory tracking for all product variants."""
    print("\n=== TASK 2: ENABLING INVENTORY TRACKING ===")

    total_variants = 0
    already_tracked = 0
    enabled_count = 0
    failed_count = 0

    for product in all_products:
        product_id = product["id"]
        product_title = product["title"]
        variants = product["variants"]["nodes"]

        for variant in variants:
            total_variants += 1
            variant_id = variant["id"]
            variant_title = variant["title"]
            inventory_item = variant.get("inventoryItem", {})

            if not inventory_item:
                print(f"  WARNING: No inventory item for variant {variant_id} in {product_title}")
                continue

            inventory_item_id = inventory_item["id"]
            is_tracked = inventory_item.get("tracked", False)

            if is_tracked:
                already_tracked += 1
                inventory_updates.append({
                    "product_id": product_id,
                    "product_title": product_title,
                    "variant_id": variant_id,
                    "variant_title": variant_title,
                    "inventory_item_id": inventory_item_id,
                    "action": "already_tracked",
                    "success": True,
                })
            else:
                print(f"  Enabling tracking: {product_title[:50]} / {variant_title}")
                success = enable_inventory_tracking(
                    inventory_item_id, product_title, variant_title
                )

                if success:
                    enabled_count += 1
                    print(f"    OK - Tracking enabled")
                    inventory_updates.append({
                        "product_id": product_id,
                        "product_title": product_title,
                        "variant_id": variant_id,
                        "variant_title": variant_title,
                        "inventory_item_id": inventory_item_id,
                        "action": "tracking_enabled",
                        "success": True,
                    })
                else:
                    failed_count += 1
                    print(f"    FAILED - Could not enable tracking")
                    inventory_updates.append({
                        "product_id": product_id,
                        "product_title": product_title,
                        "variant_id": variant_id,
                        "variant_title": variant_title,
                        "inventory_item_id": inventory_item_id,
                        "action": "tracking_enable_failed",
                        "success": False,
                    })

                time.sleep(0.2)  # Rate limiting

    print(f"\n  TASK 2 SUMMARY:")
    print(f"    Total variants processed: {total_variants}")
    print(f"    Already had tracking enabled: {already_tracked}")
    print(f"    Newly enabled tracking: {enabled_count}")
    print(f"    Failed to enable tracking: {failed_count}")


def save_results():
    """Save all results to JSON and CSV files."""
    print("\n=== SAVING RESULTS ===")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "/Users/bfjmedia4/Documents/Stefano/Personal/3DeltaDental"

    # Save drafted products to CSV
    drafted_csv_path = f"{output_dir}/drafted_products_{timestamp}.csv"
    with open(drafted_csv_path, "w", newline="", encoding="utf-8") as f:
        if drafted_products:
            fieldnames = ["product_id", "title", "previous_status", "new_status", "reason"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(drafted_products)
    print(f"  Drafted products CSV: {drafted_csv_path}")

    # Save inventory updates to CSV
    inventory_csv_path = f"{output_dir}/inventory_updates_{timestamp}.csv"
    with open(inventory_csv_path, "w", newline="", encoding="utf-8") as f:
        if inventory_updates:
            fieldnames = ["product_id", "product_title", "variant_id", "variant_title",
                         "inventory_item_id", "action", "success"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(inventory_updates)
    print(f"  Inventory updates CSV: {inventory_csv_path}")

    # Save full summary to JSON
    summary = {
        "timestamp": timestamp,
        "store": STORE,
        "drafted_products": {
            "total_no_image": len(drafted_products),
            "newly_drafted": len([p for p in drafted_products if p["reason"] == "no_images"]),
            "already_draft": len([p for p in drafted_products if p["reason"] == "no_images_already_draft"]),
            "products": drafted_products,
        },
        "inventory_updates": {
            "total_variants": len(inventory_updates),
            "already_tracked": len([u for u in inventory_updates if u["action"] == "already_tracked"]),
            "newly_enabled": len([u for u in inventory_updates if u["action"] == "tracking_enabled"]),
            "failed": len([u for u in inventory_updates if u["action"] == "tracking_enable_failed"]),
            "updates": inventory_updates,
        },
        "errors": errors,
    }

    json_path = f"{output_dir}/product_management_summary_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"  Full summary JSON: {json_path}")

    return drafted_csv_path, inventory_csv_path, json_path, summary


def main():
    print("=" * 70)
    print("  3 DELTA DENTAL - SHOPIFY PRODUCT MANAGEMENT")
    print(f"  Store: {STORE}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Fetch all products
    all_products = fetch_all_products()

    if not all_products:
        print("ERROR: No products fetched. Exiting.")
        sys.exit(1)

    # Task 1: Draft products with no images
    no_image_products = process_no_image_products(all_products)

    # Task 2: Enable inventory tracking
    process_inventory_tracking(all_products)

    # Save results
    drafted_csv, inventory_csv, json_path, summary = save_results()

    # Final summary
    print("\n" + "=" * 70)
    print("  FINAL SUMMARY")
    print("=" * 70)
    print(f"\n  TASK 1 - Products Drafted (No Images):")
    print(f"    Total products with no images:  {summary['drafted_products']['total_no_image']}")
    print(f"    Newly set to DRAFT:              {summary['drafted_products']['newly_drafted']}")
    print(f"    Already in DRAFT:                {summary['drafted_products']['already_draft']}")

    print(f"\n  TASK 2 - Inventory Tracking:")
    print(f"    Total variants processed:        {summary['inventory_updates']['total_variants']}")
    print(f"    Already tracked (unchanged):     {summary['inventory_updates']['already_tracked']}")
    print(f"    Newly enabled:                   {summary['inventory_updates']['newly_enabled']}")
    print(f"    Failed:                          {summary['inventory_updates']['failed']}")

    print(f"\n  Errors encountered: {len(errors)}")
    if errors:
        for err in errors[:10]:
            print(f"    - {err}")

    print(f"\n  Output files:")
    print(f"    {drafted_csv}")
    print(f"    {inventory_csv}")
    print(f"    {json_path}")
    print(f"\n  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
