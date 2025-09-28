from django.urls import path
from .views_expense import ExpenseListView, ExpenseCreateView

urlpatterns = [
    path('expenses/', ExpenseListView.as_view(), name='expense-list'),
    path('expenses/new/', ExpenseCreateView.as_view(), name='expense-create'),
]
