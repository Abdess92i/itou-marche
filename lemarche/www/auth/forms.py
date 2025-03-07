from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, UserCreationForm

from lemarche.users.models import User
from lemarche.utils.constants import EMPTY_CHOICE, HOW_MANY_CHOICES
from lemarche.utils.password_validation import CnilCompositionPasswordValidator


class SignupForm(UserCreationForm):
    KIND_CHOICES_FORM = (
        (User.KIND_SIAE, "Une entreprise sociale inclusive (SIAE ou structure du handicap, GEIQ)"),
        (User.KIND_BUYER, "Un acheteur"),
        (User.KIND_PARTNER, "Un partenaire (réseaux, facilitateurs)"),
    )
    FORM_PARTNER_KIND_CHOICES = EMPTY_CHOICE + User.PARTNER_KIND_CHOICES

    kind = forms.ChoiceField(label="", widget=forms.RadioSelect, choices=KIND_CHOICES_FORM, required=True)
    first_name = forms.CharField(
        label="Votre prénom", widget=forms.TextInput(attrs={"autofocus": "autofocus"}), required=True
    )
    last_name = forms.CharField(label="Votre nom", required=True)
    phone = forms.CharField(
        label="Votre numéro de téléphone",
        max_length=35,
        required=False,
    )
    # company_name is hidden by default in the frontend. Shown if the user choses kind BUYER or PARTNER
    company_name = forms.CharField(
        label="Le nom de votre structure",
        required=False,
    )
    # position is hidden by default in the frontend. Shown if the user choses kind BUYER
    position = forms.CharField(
        label="Votre poste",
        required=False,
    )
    # partner_kind is hidden by default in the frontend. Shown if the user choses kind PARTNER
    partner_kind = forms.ChoiceField(
        label=User._meta.get_field("partner_kind").verbose_name, choices=FORM_PARTNER_KIND_CHOICES, required=False
    )

    email = forms.EmailField(
        label="Votre adresse e-mail",
        widget=forms.TextInput(attrs={"placeholder": "Merci de bien vérifier l'adresse saisie."}),
        required=True,
    )
    # help_text="Nous enverrons un e-mail de confirmation à cette adresse avant de valider le compte.")
    nb_of_inclusive_provider_2022 = forms.ChoiceField(
        # flake8: noqa E501
        label="En 2022, avec combien de prestataires inclusifs relevant du secteur de l’Insertion avez-vous déjà travaillé ?",
        choices=HOW_MANY_CHOICES,
        widget=forms.RadioSelect(),
        required=False,
    )
    nb_of_handicap_provider_2022 = forms.ChoiceField(
        # flake8: noqa E501
        label="En 2022, avec combien de prestataires inclusifs relevant du secteur du Handicap avez-vous déjà travaillé ?",
        choices=HOW_MANY_CHOICES,
        widget=forms.RadioSelect(),
        required=False,
    )
    accept_rgpd = forms.BooleanField(label=User._meta.get_field("accept_rgpd").help_text, help_text="", required=True)
    # accept_survey is hidden by default in the frontend. Shown if the user choses kind BUYER or PARTNER
    accept_survey = forms.BooleanField(
        label=User._meta.get_field("accept_survey").help_text, help_text="", required=False
    )

    # accept_share_contact_to_external_partners is hidden by default in the frontend. Shown if the user choses kind SIAE  # noqa
    accept_share_contact_to_external_partners = forms.BooleanField(
        label=User._meta.get_field("accept_share_contact_to_external_partners").help_text, help_text="", required=False
    )

    class Meta:
        model = User
        fields = [
            "kind",
            "first_name",
            "last_name",
            "phone",
            "position",
            "company_name",
            "partner_kind",
            "email",
            "password1",
            "password2",
            "accept_rgpd",
            "accept_survey",
            "accept_share_contact_to_external_partners",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # password validation rules
        self.fields["password1"].help_text = CnilCompositionPasswordValidator().get_help_text()

    def clean_email(self):
        email = self.cleaned_data["email"]
        return email.lower()

    def save(self, commit=True):

        instance = super(SignupForm, self).save(commit=False)
        extra_data = {}
        if self.cleaned_data.get("nb_of_inclusive_provider_2022"):
            extra_data["nb_of_inclusive_provider_2022"] = self.cleaned_data.get("nb_of_inclusive_provider_2022")

        if self.cleaned_data.get("nb_of_handicap_provider_2022"):
            extra_data["nb_of_handicap_provider_2022"] = self.cleaned_data.get("nb_of_handicap_provider_2022")

        instance.extra_data = extra_data

        if commit:
            self.save_m2m()

            instance.save()
        return instance


class LoginForm(AuthenticationForm):
    def clean_username(self):
        username = self.cleaned_data["username"]
        return username.lower()


class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Votre adresse e-mail", required=True)
