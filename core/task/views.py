import sys
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Task
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from rest_framework.viewsets import GenericViewSet
from django.urls import reverse


# Create your views here.
class TaskListView(ListView):
    def get_queryset(self):
        tasks = Task.objects.filter(author=self.request.user.profile)
        return tasks


class TaskCreateView(CreateView, LoginRequiredMixin):
    login_url = "/accounts/login/"
    model = Task
    fields = ["title"]
    success_url = "/tasks/list/"

    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        return super().form_valid(form)


class TaskDetailView(DetailView):
    queryset = Task.objects.all()


class TaskEditView(UpdateView):
    queryset = Task.objects.all()
    fields = ["title", "status"]
    success_url = "/tasks/list/"


class TaskDeleteView(DeleteView):
    queryset = Task.objects.all()
    success_url = "/tasks/list/"


def update_status(request, pk):
    if request.method == "POST":
        obj = get_object_or_404(Task, pk=pk)
        new_status = request.POST.get("status")
        if new_status in ["NEW", "DONE"]:  # Ensure valid status
            obj.status = new_status
            obj.save()
            return redirect(reverse("tasks:task-detail", kwargs={'pk':pk}))
        else:
            return HttpResponse("Invalid status", status=400)
    return HttpResponse("Invalid request method", status=405)
