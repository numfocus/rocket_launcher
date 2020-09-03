import json

from django.http import JsonResponse
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .models import Expense, ExpensePayload


class IndexView(generic.ListView):
    template_name = 'core/expense/index.html'
    context_object_name = 'latest_expense_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Expense.objects.filter(
            submit_date__lte=timezone.now()
        ).order_by('-submit_date')[:5]


class DetailView(generic.DetailView):
    model = Expense
    template_name = 'core/expense/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


@csrf_exempt
def reimbursement_request(request):
    payload = json.loads(request.body)
    expense_payload = ExpensePayload(json=payload)
    expense_payload.save()
    expense = expense_payload.create_expense()
    expense.save()
    expense.email_finance_team()
    return JsonResponse({'status': 200, 'message': 'Expense Payload created.'})