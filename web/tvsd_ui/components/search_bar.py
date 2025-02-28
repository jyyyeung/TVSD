# <div class="field is-grouped">
#   <p class="control is-expanded">
#     <input class="input" type="text" placeholder="Find a repository">
#   </p>
#   <p class="control">
#     <a class="button is-info">
#       Search
#     </a>
#   </p>
# </div>
from crispy_bulma.layout import Button, Field, Layout
from crispy_forms.helper import FormHelper
from django import forms


class SearchBar(forms.Form):
    search = forms.CharField(
        label="Search",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "input", "type": "text", "placeholder": "Find a repository"}
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super(SearchBar, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-search-form"
        self.helper.form_method = "post"
        # self.helper.form_horizontal = True
        self.helper.layout = Layout(
            Field("search", css_class="input is-expanded"),
            Button("submit", css_class="button is-info"),
        )
