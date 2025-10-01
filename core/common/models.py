from django.db import models
from typing import Callable
from django.utils.translation import gettext_lazy as _
from .generators import default_subid_generator

class SubIDModelProtocol(models.Model):
    subid: str

    class Meta:
        abstract = True

def get_subid_model(
        *,
        max_length: int = 64,
        default: Callable[[], str] = default_subid_generator
) -> type[SubIDModelProtocol]:
    """
    Generate a Django model class with a `subid` field.

    This function dynamically creates and returns a Django model class with a `subid` field,
    which is a `CharField` with a specified maximum length and default value. The created
    model class inherits from `models.Model` and is abstract.

    Parameters
    ----------
    max_length : int, optional
        The maximum length of the `subid` field. Defaults to 64.
    default : Callable[[], str], optional
        A callable that returns the default value for the `subid` field. Defaults to
        `default_subid_generator`.

    Returns
    -------
    type[SubIDModelProtocol]
        A dynamically created Django model class with a `subid` field.

    Notes
    -----
    - The `subid` field is defined as a `CharField` with the following attributes:
        - `max_length`: Set to the value of `max_length` parameter.
        - `db_column`: Set to "subid".
        - `unique`: Set to `True`.
        - `null`: Set to `True`.
        - `blank`: Set to `True`.
        - `editable`: Set to `False`.
        - `default`: Set to the callable passed as `default` parameter.
        - `help_text`: Describes the purpose of the field as "Primary key shown to user."

    - The generated model class is abstract and cannot be instantiated directly.
    - The `__class_getitem__` method is set to `default_class_getitem`.
    """
    return type['SubIDModelProtocol'](
        "SubIDModel", (models.Model,), {
            "__module__": __name__,
            "__qualname__": "SubIDModel",
            "__class_getitem__": default_class_getitem,
            "subid": models.CharField(
                _("subid"),
                max_length=max_length,
                db_column="subid",
                unique=True,
                null=True,
                blank=True,
                editable=False,
                default=default,
                help_text=_("Primary key shown to user.")),
            "Meta": type(
                "Meta", (), {
                    "abstract": True
                }
            )
        }
    )
    
def default_class_getitem(cls, *args, **kwargs):
    return cls