# common/utils/pricing.py

from django.core.exceptions import ValidationError


def get_dynamic_item_price(
    product, fabric_type, variant_type, qty
) -> tuple[float, float]:
    """
    Determine dynamic item pricing based on product tiers, fabric type, and quantity.

    Returns:
        tuple (final_price, subtotal)
    """

    # 1️⃣ Find applicable price tier
    tier_qs = product.price_tiers.all()
    if variant_type:
        tier_qs = tier_qs.filter(variant_type=variant_type)
    else:
        tier_qs = tier_qs.filter(variant_type__isnull=True)

    tier = tier_qs.filter(min_qty__lte=qty, max_qty__gte=qty).first()

    if not tier:
        raise ValidationError(
            f"No valid price tier found for quantity {qty} on product {product.name}."
        )

    # 2️⃣ Base price
    base_price = tier.base_price or 0

    # 3️⃣ Fabric price adjustment
    fabric_price = 0
    if tier.variant_type:
        fabric_price_obj = tier.variant_type.fabric_prices.filter(
            fabric_type=fabric_type
        ).first()
        if fabric_price_obj:
            fabric_price = fabric_price_obj.price or 0

    # 4️⃣ Calculate final per-unit price and subtotal
    final_price = base_price + fabric_price
    subtotal = final_price * qty

    return final_price, subtotal


def mapping_product_qty(unit: str) -> int:
    """
    Mapping product quantity based on unit.
    """
    match unit.lower():
        case "stel":
            return 2
        case "atasan":
            return 1
        case _:
            raise ValueError(f"Invalid unit '{unit}'")
