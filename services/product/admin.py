from django.contrib import admin

# Register your models here.
from services.product.models.fabric_price import FabricPrice
from services.product.models.product import Product
from services.product.models.fabric_type import FabricType
from services.product.models.price_adjustment import ProductPriceAdjustment
from services.product.models.price_tier import ProductPriceTier
from services.product.models.variant_type import ProductVariantType

admin.site.register(Product)
admin.site.register(FabricType)
admin.site.register(FabricPrice)
admin.site.register(ProductPriceAdjustment)
admin.site.register(ProductPriceTier)
admin.site.register(ProductVariantType)
