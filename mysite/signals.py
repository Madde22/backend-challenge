from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from utils.util import delete_cache


@receiver(post_delete, sender=None, dispatch_uid='post_delete_update_cache')
def post_delete_cache(sender, instance, **kwargs):
    delete_cache(sender, instance)


@receiver(post_save, sender=None, dispatch_uid='post_save_update_cache')
def post_save_cache(sender, instance, created, raw, **kwargs):
    if raw:
        return

    if created and sender.__name__ == "Vendor":
        from product.tasks import update_vendor_statistic_task
        update_vendor_statistic_task.delay(vendor_id=instance.id)

    if sender.__name__ == "Product" or sender.__name__ == "Order":
        from product.tasks import update_vendor_statistic_task
        update_vendor_statistic_task.delay(product_id=instance.id)

    if sender.__name__ in ["Product"]:
        """
        Delete all main category es_ caches, and reset
        """
        delete_cache(sender, instance)
