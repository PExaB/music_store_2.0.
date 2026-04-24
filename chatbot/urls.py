# chatbot/urls.py
from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # path('', views.chat_page, name='chat_page'),          # главная страница чата
    path('api/chat/', views.chat_api, name='chat_api'),   # API endpoint
    path('api/chat/history/', views.get_chat_history, name='chat_history'),
]