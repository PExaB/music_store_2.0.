# store/migrations/0003_brand_and_migrate_data.py
from django.db import migrations, models
import django.db.models.deletion

def migrate_brand_data(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    Brand = apps.get_model('store', 'Brand')
    
    # Собираем уникальные бренды из существующих продуктов
    unique_brands = Product.objects.values_list('brand', flat=True).distinct()
    
    # Создаем записи брендов
    brand_map = {}
    for brand_name in unique_brands:
        if brand_name:  # Пропускаем пустые значения
            brand = Brand.objects.create(
                name=brand_name,
                description=f"Бренд {brand_name}",
                is_active=True
            )
            brand_map[brand_name] = brand
    
    # Обновляем продукты, связывая их с новыми брендами
    for product in Product.objects.all():
        if product.brand and product.brand in brand_map:
            product.brand_new = brand_map[product.brand]
            product.save()

def reverse_migrate_brand_data(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    Brand = apps.get_model('store', 'Brand')
    
    # Восстанавливаем старые названия брендов
    for product in Product.objects.filter(brand_new__isnull=False):
        product.brand = product.brand_new.name
        product.save()
    
    # Удаляем все созданные бренды
    Brand.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_initial'),
    ]

    operations = [
        # 1. Создаем модель Brand
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название бренда')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='brands/', verbose_name='Логотип')),
                ('description', models.TextField(blank=True, verbose_name='Описание бренда')),
                ('country', models.CharField(blank=True, max_length=100, verbose_name='Страна')),
                ('website', models.URLField(blank=True, verbose_name='Веб-сайт')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активный')),
            ],
            options={
                'verbose_name': 'Бренд',
                'verbose_name_plural': 'Бренды',
                'ordering': ['name'],
            },
        ),
        
        # 2. Добавляем временное поле для бренда
        migrations.AddField(
            model_name='product',
            name='brand_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='store.brand', verbose_name='Бренд'),
        ),
        
        # 3. Мигрируем данные
        migrations.RunPython(migrate_brand_data, reverse_migrate_brand_data),
        
        # 4. Удаляем старое поле brand
        migrations.RemoveField(
            model_name='product',
            name='brand',
        ),
        
        # 5. Переименовываем brand_new в brand
        migrations.RenameField(
            model_name='product',
            old_name='brand_new',
            new_name='brand',
        ),
    ]