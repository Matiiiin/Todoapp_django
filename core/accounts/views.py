from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from .models import User
from django.contrib.auth import login

# Create your views here.


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class RegisterView(CreateView):
    model = User
    fields = ["email", "password"]
    success_url = "/tasks/list"

    def form_valid(self, form):
        # Create the user instance without saving it
        user = form.save(commit=False)
        # Set the password using set_password
        user.set_password(form.cleaned_data["password"])
        # Save the user instance
        user.save()
        login(self.request, user)
        return super().form_valid(form)
