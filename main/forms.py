from django import forms
from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm, AuthenticationForm

from .models import ProductReview, UserAddressBook


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы регистрации
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields['username'].widget.attrs.update({"placeholder": 'Придумайте свой логин'})
            self.fields['email'].widget.attrs.update({"placeholder": 'Введите свой email'})
            self.fields['first_name'].widget.attrs.update({"placeholder": 'Ваше имя'})
            self.fields["last_name"].widget.attrs.update({"placeholder": 'Ваша фамилия'})
            self.fields['password1'].widget.attrs.update({"placeholder": 'Придумайте свой пароль'})
            self.fields['password2'].widget.attrs.update({"placeholder": 'Повторите свой пароль'})
            self.fields[field].widget.attrs.update({'class': 'form-control'})

            self.fields['username'].label = 'Логин'
            self.fields['first_name'].label = "Имя"
            self.fields['email'].label = "Email"
            self.fields['last_name'].label = "Фамилия"
            self.fields['password1'].label = 'Пароль'
            self.fields['password2'].label = 'Проверка пароля'


# Review Add Form
class ReviewAdd(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ('review_text', 'review_rating')


# AddressBook Add Form
class AddressBookForm(forms.ModelForm):
    class Meta:
        model = UserAddressBook
        fields = ('address', 'mobile', 'status')


# ProfileEdit
class ProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        del self.fields['password']
        self.fields['username'].label = 'Логин'
        self.fields['first_name'].label = "Имя"
        self.fields['email'].label = "Email"
        self.fields['last_name'].label = "Фамилия"


class UserLoginForm(AuthenticationForm):
    """
    Форма авторизации на сайте
    """

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы регистрации
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields['username'].widget.attrs['placeholder'] = 'Логин пользователя'
            self.fields['password'].widget.attrs['placeholder'] = 'Пароль пользователя'
            self.fields['username'].label = 'Логин'
            self.fields['password'].label = 'Пароль'
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class UserPasswordChangeForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })
