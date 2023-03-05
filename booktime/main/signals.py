from io import BytesIO
import logging
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import ProductImage

THUMBNAIL_SIZE = (300, 300)

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ProductImage)
def generate_thumbnail(sender, instance, **kwargs):
    logger.info('Generating thumbnail for product %d', instance.product.id)
    image = Image.open(instance.image)
    image = image.convert('RGB')
    image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

    temp_thumbnail = BytesIO()
    image.save(temp_thumbnail, 'JPEG')
    temp_thumbnail.seek(0)

    # Set save=False, otherwise it will run in an infinite loop
    instance.thumbnail.save(instance.image.name, ContentFile(
        temp_thumbnail.read()), save=False)
    temp_thumbnail.close()
