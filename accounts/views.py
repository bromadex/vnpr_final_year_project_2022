from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import forms, logout as auth_logout, login as auth_login
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .models import User
from .serializers import UserSerializer


class SignUpView(generic.CreateView):
    form_class = forms.UserCreationForm
    success_url = reverse_lazy('accounts:login_page')
    template_name = 'accounts/signup.html'


class LoginView(generic.FormView):
    form_class = forms.AuthenticationForm
    success_url = reverse_lazy('events:list')
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)


def logout_view(request):
    auth_logout(request)
    return HttpResponseRedirect('/')


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
