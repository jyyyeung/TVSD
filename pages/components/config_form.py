from crispy_bulma.bulma import InlineCheckboxes, InlineRadios
from crispy_bulma.layout import HTML, Field, Layout, Submit
from crispy_forms.helper import FormHelper
from django import forms
from django.conf import settings

from pages.validators import validate_path
from tvsd.sources import __all__ as SOURCE_LIST


class ConfigForm(forms.Form):
    CREATE_MEDIA_ROOT_CHOICES: list[tuple[bool, str]] = [(True, "Yes"), (False, "No")]
    CREATE_TEMP_ROOT_CHOICES: list[tuple[bool, str]] = [(True, "Yes"), (False, "No")]
    SOURCES_CHOICES: list[tuple[str, str]] = []

    for source in SOURCE_LIST:
        # Add Source to Choices
        SOURCES_CHOICES.append((source, source.upper()))

    # initial_sources: list[str] = []
    # if settings.DISABLED_SOURCES != []:
    #     # Filter Out Disabled Sources
    #     initial_sources = [x for x in SOURCE_LIST if x not in settings.DISABLED_SOURCES]

    media_root = forms.CharField(
        label="Media Root Path",
        required=True,
        initial=settings.MEDIA_ROOT,
        empty_value="/media",
        validators=[validate_path],
        help_text="Path to media storage after download is completed",
    )
    temp_root = forms.CharField(
        label="Create Media Root Path?",
        required=True,
        initial=settings.TEMP_ROOT,
        empty_value="/temp",
        validators=[validate_path],
        help_text="Path to directory for storing temp files during download",
    )
    create_media_root = forms.ChoiceField(
        label="Temp Root Path",
        widget=forms.RadioSelect,
        choices=CREATE_MEDIA_ROOT_CHOICES,
        initial=settings.CREATE_MEDIA_ROOT,
        help_text="Create <strong>media root</strong> path when it is missing?",
    )
    create_temp_root = forms.ChoiceField(
        label="Create Temp Root Path?",
        widget=forms.RadioSelect,
        initial=settings.CREATE_TEMP_ROOT,
        choices=CREATE_TEMP_ROOT_CHOICES,
        help_text="Create <strong>temp root</strong> path when it is missing?",
    )
    sources = forms.MultipleChoiceField(
        label="Enable Sources",
        widget=forms.CheckboxSelectMultiple,
        choices=SOURCES_CHOICES,
        initial=settings.SOURCES,
    )

    def __init__(self, *args, **kwargs) -> None:
        super(ConfigForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-config-form"
        self.helper.form_method = "post"
        self.helper.form_horizontal = True
        self.helper.add_input(Submit("submit", "Save Settings"))
        self.helper.layout = Layout(
            HTML("""<div class="divider">Media Root</div>"""),
            Field("media_root", css_class="form-control"),
            InlineRadios("create_media_root", css_class="form-control is-checkradio"),
            HTML("""<div class="divider">Temp Root</div>"""),
            Field("temp_root", css_class="form-control"),
            InlineRadios("create_temp_root", css_class="form-control is-checkradio"),
            HTML("""<div class="divider">Sources</div>"""),
            InlineCheckboxes("sources", css_class="form-control is-checkradio"),
        )
