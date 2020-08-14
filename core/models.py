from django.db import models


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
    is_staff = models.BooleanField()

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


class ProjectFinancialTeam(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    members = models.ManyToManyField(ProjectMember)
    email = models.EmailField(null=True)


class ExpensePayload(models.Model):
    """Payload for Expenses"""
    json = models.JSONField()


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
    receipts_url = models.URLField()
    payee_name = models.CharField(max_length=200)
    additional_comments = models.TextField()
    street_address_1 = models.CharField(max_length=200)
    street_address_2 = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=200)
    payment_method = models.CharField(
        max_length=2,
        choices=PaymentTypes.choices,
        default=PaymentTypes.NOT_PROVIDED,
    )
    ach_account_holder = models.CharField(max_length=200)
    ach_routing_number = models.CharField(max_length=200)
    ach_account_number = models.CharField(max_length=200)
    ach_account_type = models.CharField(max_length=200)
    wire_bank_id = models.CharField(max_length=200)
    wire_bank_name = models.CharField(max_length=200)
    wire_bank_address = models.CharField(max_length=200)
    wire_account_holder = models.CharField(max_length=200)
    wire_iban = models.CharField(max_length=200)
    paypal_email = models.EmailField()
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
