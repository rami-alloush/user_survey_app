# from crispy_forms.helper import FormHelper
from django import forms
from .models import Course


class CourseSelectForm(forms.Form):
    course_name = forms.ModelChoiceField(
        empty_label="Select Course",
        queryset=Course.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control', 'label_from_instance ': 'dd'})
    )

    def __init__(self, *args, **kwargs):
        super(CourseSelectForm, self).__init__(*args, **kwargs)
        self.fields['course_name'].label = ''
