from asgiref.sync import sync_to_async

from wardrobe.models import ClothingItem


@sync_to_async
def get_all_clothes():
    return list(ClothingItem.objects.all())
