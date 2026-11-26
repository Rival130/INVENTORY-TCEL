from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from modules.categories.models import Category
from modules.products.models import Product
from modules.warehouse.models import Warehouse

from .forms import StockForm, StockMovementForm
from .models import Stock, StockMovement


class StockMovementViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="stock-user",
            password="test-password",
        )
        self.client.force_login(user)

    def test_movement_list_uses_existing_template(self):
        response = self.client.get(reverse("stock:movement_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stock/stock_movement_list.html")

    def test_movement_create_uses_existing_template(self):
        response = self.client.get(reverse("stock:movement_create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stock/stock_movement_form.html")


class StockFormTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Test category")
        self.product = Product.objects.create(
            sku="TEST-001",
            name="Test product",
            category=category,
        )
        self.warehouse = Warehouse.objects.create(name="Test warehouse")

    def test_create_stock_records_initial_adjustment(self):
        form = StockForm(
            data={
                "product": self.product.pk,
                "warehouse": self.warehouse.pk,
                "quantity": 5,
                "note": "Opening balance",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        stock = form.save()

        self.assertEqual(stock.quantity, 5)
        movement = StockMovement.objects.get()
        self.assertEqual(movement.movement_type, "adjust")
        self.assertEqual(movement.quantity, 5)
        self.assertEqual(movement.note, "Opening balance")

    def test_update_stock_records_quantity_difference(self):
        stock = Stock.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            quantity=5,
        )
        form = StockForm(
            data={
                "product": self.product.pk,
                "warehouse": self.warehouse.pk,
                "quantity": 3,
                "note": "Correction",
            },
            instance=stock,
        )

        self.assertTrue(form.is_valid(), form.errors)
        stock = form.save()

        self.assertEqual(stock.quantity, 3)
        movement = StockMovement.objects.get()
        self.assertEqual(movement.movement_type, "adjust")
        self.assertEqual(movement.quantity, -2)
        self.assertEqual(movement.note, "Correction")


class StockMovementFormTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Test category")
        self.product = Product.objects.create(
            sku="TEST-001",
            name="Test product",
            category=category,
        )
        self.warehouse = Warehouse.objects.create(name="Test warehouse")

    def test_create_movement_updates_stock_and_records_movement(self):
        form = StockMovementForm(
            data={
                "movement_type": "in",
                "product": self.product.pk,
                "warehouse": self.warehouse.pk,
                "quantity": 5,
                "reference": "INV-001",
                "note": "Received",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        movement = form.save()

        self.assertEqual(movement.quantity, 5)
        self.assertEqual(movement.reference, "INV-001")
        self.assertEqual(
            Stock.objects.get(product=self.product, warehouse=self.warehouse).quantity,
            5,
        )

    def test_incoming_movement_rejects_non_positive_quantity(self):
        form = StockMovementForm(
            data={
                "movement_type": "in",
                "product": self.product.pk,
                "warehouse": self.warehouse.pk,
                "quantity": 0,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)
