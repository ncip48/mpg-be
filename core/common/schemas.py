from drf_yasg.inspectors import SwaggerAutoSchema

class CustomAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys=None):
        # First check overrides (e.g., @swagger_auto_schema(tags=...))
        tags = self.overrides.get("tags", None)

        # Otherwise check for custom attribute on the view
        if not tags:
            tags = getattr(self.view, "my_tags", [])

        # Fallback: use the first part of the path (operation_keys[0])
        if not tags:
            tags = [operation_keys[0]]

        return tags
