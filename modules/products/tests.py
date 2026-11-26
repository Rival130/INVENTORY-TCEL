from django.test import TestCase

from django.urls import reverse

from modules.categories.models import Category
from modules.products.models import Product
from modules.users.models import User


class ProductViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="password")
        self.client.force_login(self.user)

    def test_home_page_renders(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)

    def test_products_page_renders(self):
        response = self.client.get(reverse("products:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("products:create"))

    def test_add_product_page_renders(self):
        response = self.client.get(reverse("products:create"))

        self.assertEqual(response.status_code, 200)

    def test_add_product_saves_valid_product(self):
        category = Category.objects.create(name='Accessories')

        response = self.client.post(
            reverse('products:create'),
            {
                'sku': 'ACC-001',
                'name': 'USB Cable',
                'category': category.pk,
                'description': '',
                'unit': 'pcs',
                'purchase_price': '2.50',
                'selling_price': '5.00',
                'min_stock': '0',
                'is_active': 'on',
            },
        )

        self.assertRedirects(response, reverse("products:list"))
        self.assertTrue(Product.objects.filter(sku='ACC-001').exists())
