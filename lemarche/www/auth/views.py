from django.contrib import messages
from django.contrib.auth import authenticate, login, views as auth_views
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView

from lemarche.users.models import User
from lemarche.utils.urls import get_safe_url
from lemarche.www.auth.forms import LoginForm, PasswordResetForm, SignupForm
from lemarche.www.auth.tasks import add_to_contact_list, send_signup_notification_email


class LoginView(auth_views.LoginView):
    template_name = "auth/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True
    # success_url = settings.LOGIN_REDIRECT_URL  # see get_success_url() below

    def get(self, request, *args, **kwargs):
        """Check if there is any custom message to display."""
        message = request.GET.get("message", None)
        # Users need to be logged in to download the search results in CSV
        if message == "login-to-download":
            messages.add_message(request, messages.INFO, "Vous devez être connecté pour télécharger la liste.")
        if message == "login-to-favorite":
            messages.add_message(request, messages.INFO, "Vous devez être connecté pour créer des listes d'achats.")
        if message == "login-to-display-contacts":
            messages.add_message(request, messages.INFO, "Vous devez être connecté pour afficher les coordonnées.")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        - Show post-migration message to existing users (they need to reset their password).
        - Get next param to append to the signup url
        """
        context = super().get_context_data(**kwargs)
        email = self.request.POST.get("username", "")
        if email:
            user = User.objects.filter(email=email.lower()).first()
            if user:
                context["email_exists_password_empty"] = True if not getattr(user, "password", "") else False
        next_url = self.request.GET.get("next", None)
        if next_url:
            context["next_param"] = f"?next={next_url}"
        return context

    def get_success_url(self):
        """
        Redirect to:
        - next_url if there is a next param
        - or dashboard if SIAE
        """
        success_url = super().get_success_url()
        next_url = self.request.GET.get("next", None)
        # sanitize next_url
        if next_url:
            safe_url = get_safe_url(self.request, param_name="next")
            if safe_url:
                return safe_url
        elif self.request.user.kind == User.KIND_SIAE:
            return reverse_lazy("dashboard:home")
        return success_url


class SignupView(SuccessMessageMixin, CreateView):
    template_name = "auth/signup.html"
    form_class = SignupForm
    # success_url = reverse_lazy("wagtail_serve", args=("",))  # # doesn't work + see get_success_url() below
    success_message = "Inscription validée !"  # see get_success_message() below

    def form_valid(self, form):
        """
        - send a welcome email to the user
        - send a notification email to the staff
        - login the user automatically
        - track signup
        """
        user = form.save()
        # add to Mailjet list (to send welcome email + automation)
        add_to_contact_list(user, "signup")
        # signup notification email for the team
        send_signup_notification_email(user)
        # login the user
        user = authenticate(username=form.cleaned_data["email"], password=form.cleaned_data["password1"])
        login(self.request, user)
        # response
        messages.add_message(self.request, messages.SUCCESS, self.get_success_message(form.cleaned_data))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """
        Redirect to:
        - next_url if there is a next param
        - or dashboard if SIAE
        """
        success_url = reverse_lazy("wagtail_serve", args=("",))
        next_url = self.request.GET.get("next", None)
        # sanitize next_url
        if next_url:
            safe_url = get_safe_url(self.request, param_name="next")
            if safe_url:
                return safe_url
        elif self.request.POST.get("kind") == User.KIND_SIAE:
            return reverse_lazy("dashboard:home")
        return success_url

    def get_success_message(self, cleaned_data):
        """Show detailed welcome message to SIAE."""
        success_message = super().get_success_message(cleaned_data)
        if cleaned_data["kind"] == User.KIND_SIAE:
            success_message += mark_safe(
                "<br />Vous pouvez maintenant ajouter votre structure en cliquant sur "
                f"<a href=\"{reverse_lazy('dashboard:siae_search_by_siret')}\">Ajouter une structure</a>."
            )
        return success_message


class PasswordResetView(auth_views.PasswordResetView):
    template_name = "auth/password_reset.html"
    form_class = PasswordResetForm
    success_url = reverse_lazy("auth:password_reset_sent")  # see get_success_url() below
    email_template_name = "auth/password_reset_email_body.html"
    subject_template_name = "auth/password_reset_email_subject.txt"

    def get_success_url(self):
        success_url = super().get_success_url()
        user_email = self.request.POST.get("email")
        return f"{success_url}?email={user_email}"
