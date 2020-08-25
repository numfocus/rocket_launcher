from django.urls import path

from . import views

app_name = 'rocket_launcher_core'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('reimbursement_request', views.reimbursement_request, name='reimbursement_request'),
]