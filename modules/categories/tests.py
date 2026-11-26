from django.db.models import Count
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from modules.categories.models import Category
from modules.products.models import Product


class CategoryURLTests(SimpleTestCase):
    def test_category_urls_are_namespaced(self):
        self.assertEqual(reverse("categories:category_list"), "/categories/")
        self.assertEqual(reverse("categories:category_create"), "/categories/create/")
        self.assertEqual(reverse("categories:category_update", args=[1]), "/categories/1/update/")
        self.assertEqual(reverse("categories:category_delete", args=[1]), "/categories/1/delete/")

    def test_homepage_renders_categories_navigation(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/categories/"')


class CategoryProductCountTests(TestCase):
    def test_categories_can_be_annotated_with_product_count(self):
        category = Category.objects.create(name="Office")
        Product.objects.create(
            sku="OFFICE-001",
            name="Notebook",
            category=category,
        )

        category_with_count = Category.objects.annotate(
            product_count=Count("products")
        ).get(pk=category.pk)

        self.assertEqual(category_with_count.product_count, 1)
