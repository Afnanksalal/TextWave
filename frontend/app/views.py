# app/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .flask_api import process_text
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm


def index(request):
    return render(request, 'index.html')


@login_required
def process_request_view(request):
    if request.method == 'POST':
        text_input = request.POST.get('text_input')
        language = request.POST.get('language', 'EN')
        accent = request.POST.get('accent', 'EN-Default')
        speed = float(request.POST.get('speed', 1.0))
        pitch = int(request.POST.get('pitch', 0))
        volume = int(request.POST.get('volume', 0))
        reference_audio = request.FILES.get('reference_audio')

        response = process_text(text_input, language, accent, speed, pitch,
                                volume, reference_audio)

        if response.status_code == 200:
            return HttpResponse(response.content, content_type='audio/wav')
        else:
            return JsonResponse(response.json(), status=response.status_code)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
