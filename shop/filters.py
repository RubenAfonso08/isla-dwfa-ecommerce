import django_filters as df

from .models import Product


class ProductFilter(df.FilterSet):
    min_price = df.NumberFilter(
        field_name="price",
        lookup_expr="gte",
    )
    max_price = df.NumberFilter(
        field_name="price",
        lookup_expr="lte",
    )

    class Meta:
        model = Product
        fields = ["category", "is_active"]