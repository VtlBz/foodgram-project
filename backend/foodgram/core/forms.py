from django.forms import BaseInlineFormSet, ValidationError


class RecipeIngridientFormSet(BaseInlineFormSet):
    def clean(self):
        to_delete = 0
        for form in self.forms:
            if form.cleaned_data['DELETE']:
                to_delete += 1
        if (len(self.forms) - to_delete) == 0:
            raise ValidationError('Ингридиентов не может быть меньше 1')
        super().clean()
