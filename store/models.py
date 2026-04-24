from django.db import models
from django.conf import settings


SKILL_LEVEL_CHOICES = (
    ('beginner', 'Новичок'),
    ('amateur', 'Любитель'),
    ('professional', 'Профессионал'),
)

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название бренда")
    logo = models.ImageField(upload_to="brands/", blank=True, null=True, verbose_name="Логотип")
    description = models.TextField(blank=True, verbose_name="Описание бренда")
    country = models.CharField(max_length=100, blank=True, verbose_name="Страна")
    website = models.URLField(blank=True, verbose_name="Веб-сайт")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    
    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Категория")
    image = models.ImageField(upload_to="categories/", blank=True, null=True, verbose_name="Изображение категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, 
                             related_name='children', verbose_name="Родительская категория")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    skill_level = models.CharField(
        max_length=20,
        choices=SKILL_LEVEL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Уровень подготовки"
    )

    INSTRUMENT_TYPES = (
        ('guitar', 'Гитары'),
        ('piano', 'Клавишные'),
        ('drums', 'Ударные'),
        ('violin', 'Струнные'),
        ('wind', 'Духовые'),
        ('equipment', 'Оборудование'),
        ('accessories', 'Аксессуары'),
    )

    CONDITION_CHOICES = (
        ('new', 'Новый'),
        ('used', 'Б/У'),
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Категория")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, 
                            related_name="products", verbose_name="Бренд")
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Старая цена")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="Основное изображение")
    
    # Дополнительные поля для музыкальных инструментов
    instrument_type = models.CharField(max_length=20, choices=INSTRUMENT_TYPES, verbose_name="Тип инструмента")
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='new', verbose_name="Состояние")
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    
    # Технические характеристики
    features = models.TextField(blank=True, verbose_name="Характеристики")
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name="Вес (кг)")
    dimensions = models.CharField(max_length=100, blank=True, verbose_name="Габариты")
    
    # Мета-данные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        if self.brand:
            return f"{self.brand.name} {self.name}"
        return self.name

    @property
    def is_on_sale(self):
        return self.old_price and self.old_price > self.price

    @property
    def discount_percentage(self):
        if self.is_on_sale:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="Товар")
    image = models.ImageField(upload_to="products/gallery/", verbose_name="Изображение")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Альтернативный текст")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ['order']

    def __str__(self):
        return f"Изображение для {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "В обработке"),
        ("paid", "Оплачено"),
        ("shipped", "Отправлено"),
        ("delivered", "Доставлено"),
        ("cancelled", "Отменено"),
    )

    PAYMENT_CHOICES = (
        ("card", "Банковская карта"),
        ("cash", "Наличные курьеру"),
        ("transfer", "Банковский перевод"),
        ("sbp", "СБП"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь"
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name="ФИО",
        default="Не указано"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус"
    )

    # Информация о доставке
    shipping_address = models.TextField(
        verbose_name="Адрес доставки",
        default="Адрес не указан"
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
        default="Не указан"
    )
    email = models.EmailField(
        verbose_name="Email",
        default="customer@example.com"
    )

    # Оплата
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="card",
        verbose_name="Способ оплаты"
    )

    # Стоимость
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Промежуточный итог"
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Стоимость доставки"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Общая сумма"
    )

    # Комментарии
    notes = models.TextField(
        blank=True,
        verbose_name="Комментарии к заказу"
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} ({self.user.username})"

    def save(self, *args, **kwargs):
        self.total = self.subtotal + self.shipping_cost
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу", default=0)

    class Meta:
        verbose_name = "Отчет и аналитика"
        verbose_name_plural = "Отчет и аналитика"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.price


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Товар")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Рейтинг")
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = ['product', 'user']

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.name}"