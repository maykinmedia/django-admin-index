from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def validate_translation_json_format(value):
    if not isinstance(value, dict):
        raise ValidationError(
            _("The format of translations needs to be a JSON-object.")
        )

    language_codes = [item[0] for item in settings.LANGUAGES]
    for key, val in value.items():
        if key not in language_codes:
            raise ValidationError(
                _("The language code '{language_code}' is not enabled.").format(
                    language_code=key
                )
            )

        if not isinstance(val, str):
            raise ValidationError(
                _(
                    "The translation for language '{language_code}' is not a string."
                ).format(language_code=key)
            )


class TranslationsMixin(models.Model):
    translations = models.JSONField(
        _("translations"),
        default=dict,
        help_text=_(
            'A JSON-object that uses the Django language code as key and the localized name as value. If no translation can be found for the active language, the name is used as fallback. Example: {"en": "File", "nl": "Bestand"}'
        ),
        validators=[validate_translation_json_format],
    )

    class Meta:
        abstract = True
