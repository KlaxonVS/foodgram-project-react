from django import forms

from .models import User


class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
# аккаунт я сделал, а о том что у кастомной модели
# нужно форму задать иначе пароль не хешиться и не работает -- не знал
