from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import models
from price_parser import Price


class EmailTemplate(models.Model):
    name = models.CharField(max_length=200)
    template = models.TextField()


class Project(models.Model):
    class ProjectTypes(models.TextChoices):
        FULLY_SPONSORED = 'F'
        GRANTOR_GRANTEE = 'G'
        AFFILIATED = 'A'
        UNSPECIFIED = 'U'
    name = models.CharField(max_length=200)
    join_date = models.DateField('date joined')
    project_type = models.CharField(
        max_length=2,
        choices=ProjectTypes.choices,
        default=ProjectTypes.UNSPECIFIED,
    )

    def __str__(self):
        return self.name


class ProjectMember(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


class FinancialTeam(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    members = models.ManyToManyField(ProjectMember)
    email = models.EmailField(null=True)
    finance_sheet = models.URLField(null=True)
    email_template = models.ForeignKey('EmailTemplate', null=True, on_delete=models.SET_NULL)


class ExpensePayload(models.Model):
    """Payload for Expenses"""
    json = models.JSONField()

    def create_expense(self):
        project_name = self.json['field_NvweuLqiLo6j']
        total_amount = Price.fromstring(self.json['field_yATiGkrJo6H3'])
        project = Project.objects.get(name=project_name)
        submitter_name = self.json['field_Lq2p858JwwDY']
        submitter_email = self.json['field_rzAFVjNIJB6f']
        payment_method_str = self.json['field_1oqZp7Z9PooA']
        if payment_method_str=='Paypal':
            payment_method = Expense.PaymentTypes.PAYPAL
        else:
            payment_method = Expense.PaymentTypes.NOT_PROVIDED
        try:
            submitter = ProjectMember.objects.get(email=submitter_email)
        except ObjectDoesNotExist:
            submitter = ProjectMember(full_name=submitter_name, email=submitter_email)
            submitter.save()

        return Expense(
            additional_comments=self.json['field_zZrfMtbmmPkx'],
            city=self.json['field_PLUHGdValPnt'],
            expense_description=self.json['field_slfa1YMlonrG'],
            payee_name=self.json['field_K4vHIxUFsgmk'],
            payment_method=payment_method,
            postal_code=self.json['field_kM3mTBzGrxrl'],
            project=project,
            raw_payload=self,
            receipts_url=self.json['field_TjacJ4nxVvyJ'],
            reason=self.json['field_ewgCjybmYp39'],
            street_address_1=self.json['field_C454b5eVX0Ep'],
            state=self.json['field_5XVjaG56SWJl'],
            submit_date=date.today(),
            submitter=submitter,
            total_amount=total_amount.amount,
            total_amount_currency=total_amount.currency,
        )


class Expense(models.Model):
    class PaymentTypes(models.TextChoices):
        NOT_PROVIDED = 'N'
        ACH = 'A'
        WIRE = 'W'
        PAYPAL = 'P'
    raw_payload = models.ForeignKey(ExpensePayload, null=True, on_delete=models.SET_NULL)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    submitter = models.ForeignKey(
        ProjectMember,
        on_delete=models.PROTECT,
        related_name='submitter',
    )
    reason = models.CharField(max_length=1024)
    expense_description = models.TextField()
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    total_amount_currency = models.CharField(max_length=5, null=True)
    receipts_url = models.URLField()
    payee_name = models.CharField(max_length=200)
    additional_comments = models.TextField()
    street_address_1 = models.CharField(max_length=200)
    street_address_2 = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=200)
    payment_method = models.CharField(
        max_length=2,
        choices=PaymentTypes.choices,
        default=PaymentTypes.NOT_PROVIDED,
    )
    ach_account_holder = models.CharField(max_length=200, null=True)
    ach_routing_number = models.CharField(max_length=200, null=True)
    ach_account_number = models.CharField(max_length=200, null=True)
    ach_account_type = models.CharField(max_length=200, null=True)
    wire_bank_id = models.CharField(max_length=200, null=True)
    wire_bank_name = models.CharField(max_length=200, null=True)
    wire_bank_address = models.CharField(max_length=200, null=True)
    wire_account_holder = models.CharField(max_length=200, null=True)
    wire_iban = models.CharField(max_length=200, null=True)
    paypal_email = models.EmailField(null=True)
    submit_date = models.DateField('date submitted')
    approved = models.BooleanField(default=False)
    approver = models.ForeignKey(
        ProjectMember,
        on_delete=models.PROTECT,
        related_name='approver',
        null=True,
    )
    approval_notes = models.TextField()

    def __str__(self):
        return f'Expense from {self.project_member} submitted {self.submit_date}'

    def email_finance_team(self):
        subject = f'New Finance request for {self.project.name}'
        message = self.project.financialteam.email_template.format({
            'financial_sheet': self.project.finance_sheet,
            **self.__dict__
        })
        send_mail(
            subject,
            message,
            'rocket_launcher_bot@numfocus.org',
            [self.project.financialteam.email],
        )
