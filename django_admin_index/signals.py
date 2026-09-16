from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import AppGroup


@receiver(pre_delete, sender=AppGroup, dispatch_uid="admin_index_promote_children")
def promote_children_of_deleted_group(sender, instance, **kwargs):
    """
    Move the children of a group that is being deleted to the end of the top level.

    The ``parent`` field uses ``on_delete=SET_NULL``, which promotes the children
    with a bulk update that keeps their sibling-relative ``order`` values. Those
    values collide with the existing top-level groups and break moving groups up
    and down. Saving each child without a parent instead lets django-ordered-model
    append it to the top-level sequence, in the children's own order.
    """
    for child in list(instance.children.all()):
        child.parent = None
        child.save()
