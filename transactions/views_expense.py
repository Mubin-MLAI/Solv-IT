from django.shortcuts import render, redirect
from django.views import View
from .models_expense import Expense
from django.urls import reverse
from django.db.models import Sum, Q
from datetime import datetime, timedelta, date
from django.utils.timezone import now
from django.core.paginator import Paginator

class ExpenseListView(View):
    def get(self, request):
        expenses = Expense.objects.all().order_by('-date')
        # Filtering
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        category = request.GET.get('category')
        name = request.GET.get('name')
        if start_date:
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)
        if category and category != 'all':
            expenses = expenses.filter(category=category)
        if name:
            expenses = expenses.filter(name__icontains=name)

        # Pagination
        page_number = request.GET.get('page')
        paginator = Paginator(expenses, 10)
        page_obj = paginator.get_page(page_number)

        # Totals
        today = date.today()
        first_day_of_month = today.replace(day=1)
        first_day_of_week = today - timedelta(days=today.weekday())
        totals = {
            'month': Expense.objects.filter(date__gte=first_day_of_month).aggregate(total=Sum('amount'))['total'] or 0,
            'week': Expense.objects.filter(date__gte=first_day_of_week).aggregate(total=Sum('amount'))['total'] or 0,
            'day': Expense.objects.filter(date=today).aggregate(total=Sum('amount'))['total'] or 0,
        }
        filtered_total = expenses.aggregate(total=Sum('amount'))['total'] or 0

        # For category dropdown
        categories = list(Expense.CATEGORY_CHOICES)
        # Add any custom categories
        custom_cats = Expense.objects.values_list('category', flat=True).distinct()
        for cat in custom_cats:
            if cat not in dict(categories):
                categories.append((cat, cat.title()))

        return render(request, 'transactions/expense_list.html', {
            'expenses': page_obj,
            'page_obj': page_obj,
            'totals': totals,
            'filtered_total': filtered_total,
            'categories': categories,
            'selected_category': category or 'all',
            'start_date': start_date or '',
            'end_date': end_date or '',
            'name': name or '',
        })

class ExpenseCreateView(View):
    def get(self, request):
        return render(request, 'transactions/expense_form.html')

    def post(self, request):
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        new_category = request.POST.get('new_category')
        description = request.POST.get('description')
        date_val = request.POST.get('date')
        if category == 'other' and new_category:
            category = new_category
        Expense.objects.create(name=name, amount=amount, category=category, description=description, date=date_val)
        return redirect(reverse('expense-list'))
