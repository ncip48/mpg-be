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


def mapping_product_sum(unit: str) -> int:
    """
    Mapping product quantity (bobot) based on product name.
    """
    match unit.lower():
        case "atasan":
            return 1
        case "stel":
            return 2
        case "polo atasan":
            return 2
        case "polo stel":
            return 3
        case "baseball atasan":
            return 1
        case "baseball stel":
            return 2
        case "nrl atasan":
            return 1
        case "nrl stel":
            return 2
        case "atasan bb":
            return 2
        case "stelan bb":
            return 3
        case "celana":
            return 1
        case "ss":
            return 1
        case "atasan berlengan":
            return 1
        case "polo":
            return 2
        case "stel berlengan":
            return 2
        case "ss lengan panjang":
            return 1
        case "ss lengan pendek":
            return 1
        case "atasan lengan panjang":
            return 1
        case "sample":
            return 1
        case "atasan oversize":
            return 1
        case "baseball":
            return 1
        case _:
            return 1


def get_qty(unit: str, qty: int | float):
    return mapping_product_sum(unit) * qty


def get_qty_value(unit: str | None, qty: int | float) -> float:
    """
    Returns computed quantity based on mapping multiplier.
    If unit is None, uses multiplier 1.
    """
    if not unit:
        return qty
    return mapping_product_sum(unit) * qty
