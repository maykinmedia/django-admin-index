from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.translation import gettext as _

from django_admin_index.translations import validate_translation_json_format


class ValidatorsTests(TestCase):
    def test_valid_json_obj_success(self):
        self.assertIsNone(
            validate_translation_json_format({"en": "My profile", "nl": "Mijn profiel"})
        )

    def test_not_dict_value_fails(self):
        self.assertRaisesMessage(
            ValidationError,
            _("The format of translations needs to be a JSON-object."),
            validate_translation_json_format,
            "not a dict",
        )

    def test_disabled_language_fails(self):
        self.assertRaisesMessage(
            ValidationError,
            _("The language code '{language_code}' is not enabled.").format(
                language_code="es"
            ),
            validate_translation_json_format,
            {"es": "Mi perfil"},
        )

    def test_not_str_translation_text_fails(self):
        self.assertRaisesMessage(
            ValidationError,
            _("The translation for language '{language_code}' is not a string.").format(
                language_code="en"
            ),
            validate_translation_json_format,
            {"en": 2},
        )
