from django.contrib import admin

from .models import EmailTemplate, Expense, Project, ProjectMember, FinancialTeam


class EmailTemplateAdmin(admin.ModelAdmin):
    pass


class ExpenseAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Submission information',
         {'fields': [
             'submit_date', 'project', 'submitter'
         ]}),
        ('Expense Information',
         {'fields': [
             'reason', 'expense_description', 'total_amount', 'receipts_url',
         ]}),
        ('Payee Information',
         {'fields': [
             'payee_name', 'additional_comments', 'street_address_1', 'street_address_2',
             'city', 'state', 'postal_code', 'country', 'payment_method',
         ]}),
        ('ACH/Direct Pay',
         {'fields': [
             'ach_account_holder', 'ach_routing_number', 'ach_account_number',
             'ach_account_type'
         ]}),
        ('Wire Info',
         {'fields': [
             'wire_bank_id', 'wire_bank_name', 'wire_bank_address',
             'wire_account_holder', 'wire_iban',
         ]}),
        ('Paypal Info',
         {'fields': [
             'paypal_email',
         ]}),
        ('Approval information',
         {'fields': [
             'approver', 'approved', 'approval_notes'
         ]}),
    ]
    list_display = ('project', 'submit_date', 'reason', 'total_amount')
    list_filter = ['submit_date']


class FinancialTeamAdmin(admin.TabularInline):
    model = FinancialTeam


class ProjectAdmin(admin.ModelAdmin):
    inlines = [FinancialTeamAdmin]


class ProjectMemberAdmin(admin.ModelAdmin):
    pass


admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectMember, ProjectMemberAdmin)
