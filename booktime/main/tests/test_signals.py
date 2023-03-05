from django.test import TestCase
from main import models
from django.core.files.images import ImageFile
from decimal import Decimal


class TestSignal(TestCase):
    def test_thumbnails_are_generated_on_save(self):
        dummy_product = models.Product(
            name='The cathedral and the bazaar',
            price=Decimal('10.00'),
        )
        dummy_product.save()

        with open('main/fixtures/the-cathedral-the-bazaar.jpg', 'rb') as image_file:
            dummy_image = models.ProductImage(
                product=dummy_product,
                image=ImageFile(image_file, name='tctb.jpg'),
            )

            with self.assertLogs('main', level='INFO') as cm:
                dummy_image.save()
        
        self.assertGreaterEqual(len(cm.output), 1)
        dummy_image.refresh_from_db()

        with open('main/fixtures/the-cathedral-the-bazaar_thumb.jpg', 'rb') as thumbnail_file:
            expected_content = thumbnail_file.read()
            actual_content = dummy_image.thumbnail.read()
            assert actual_content == expected_content

        dummy_image.thumbnail.delete(save=False)
        dummy_image.image.delete(save=False)