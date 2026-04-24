from django.contrib import admin
from .models import Brand, Category, Product, ProductImage, Order, OrderItem, Review
from django.db.models import Sum, F
from rangefilter.filters import DateRangeFilterBuilder
from admin_totals.admin import ModelAdminTotals
from django.utils.formats import number_format


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "is_active", "website")
    list_filter = ("country", "is_active")
    search_fields = ("name", "country", "description")
    list_editable = ("is_active",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "price", "in_stock", "stock_quantity", "created_at")
    list_filter = ("brand", "category", "instrument_type", "condition", "is_active")
    search_fields = ("name", "brand__name", "description")
    list_editable = ("price", "in_stock", "stock_quantity")

admin.site.register(ProductImage)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "status", "payment_method",
                    "total", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("full_name", "user__username", "email", "phone")
    readonly_fields = ("created_at", "updated_at", "subtotal", "shipping_cost", "total")

    fieldsets = (
        ("Основное", {
            "fields": ("user", "full_name", "status", "payment_method")
        }),
        ("Контакты и доставка", {
            "fields": ("shipping_address", "phone", "email")
        }),
        ("Суммы", {
            "fields": ("subtotal", "shipping_cost", "total")
        }),
        ("Прочее", {
            "fields": ("notes", "created_at", "updated_at")
        }),
    )


@admin.register(OrderItem)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'order_created',
        'product_name',
        'product_category',
        'product_brand',
        'quantity',
        'price',
        'total_price',
    )
    list_filter = (
        ('order__created_at', DateRangeFilterBuilder()),
        'order__status',
        'product__category',
        'product__brand',
    )
    search_fields = (
        'product__name',
        'product__category__name',
        'product__brand__name',
        'order__user__username',
    )
    date_hierarchy = 'order__created_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs.filter(order__status__in=['paid', 'shipped', 'delivered'])
              .select_related('product', 'product__category', 'product__brand', 'order')
              .annotate(order_created=F('order__created_at'),
                        total_sum=F('quantity') * F('price'))
        )

    @admin.display(ordering='order__created_at', description='Дата заказа')
    def order_created(self, obj):
        return obj.order.created_at

    @admin.display(ordering='product__name', description='Товар')
    def product_name(self, obj):
        return obj.product.name

    @admin.display(ordering='product__category__name', description='Категория')
    def product_category(self, obj):
        return obj.product.category.name

    @admin.display(ordering='product__brand__name', description='Бренд')
    def product_brand(self, obj):
        return obj.product.brand.name if obj.product.brand else '-'

    @admin.display(ordering='total_sum', description='Сумма')
    def total_price(self, obj):
        return f"{number_format(obj.total_sum, decimal_pos=2, use_l10n=True)} руб."

    # СЮДА: считаем итоги по текущему queryset
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        totals = qs.aggregate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('price')),
        )
        response.context_data['totals'] = totals
        return response
    
admin.site.register(Review)