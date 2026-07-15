from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    age = models.IntegerField()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.name


class FileModel(models.Model):
    name = models.CharField(max_length=255)
    file_data = models.BinaryField()

    class Meta:
        db_table = 'files'


class Order(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, db_column='user_id')
    order_date = models.DateTimeField(auto_now_add=True, db_column='order_date')
    status = models.CharField(max_length=20, default='Pending', db_column='status')
    products = models.ManyToManyField('Product', through='OrderProduct')

    class Meta:
        db_table = 'orders'


class Product(models.Model):
    name = models.CharField(max_length=100, db_column='name')
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column='price')
    stock = models.PositiveIntegerField(db_column='stock')

    class Meta:
        db_table = 'products'


class OrderProduct(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_products', db_column='order_id', primary_key=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, db_column='product_id')
    quantity = models.PositiveIntegerField(db_column='quantity')

    class Meta:
        db_table = 'order_products'
        unique_together = ('order', 'product')



