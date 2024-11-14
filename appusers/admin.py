from django.contrib import admin
from .models import  *
# Register your models here.





admin.site.register(userprofile)
admin.site.register(Deposit)
admin.site.register(PIN)
admin.site.register(LocalWithdrawal)
admin.site.register(KYC)
admin.site.register(Withdraw)
admin.site.register(LoanRequest)
admin.site.register(Contact)



class TransactionHistoryAdmin(admin.ModelAdmin):
    # Define the fields or fieldsets including the timestamp field
    fields = ('user', 'amount', 'transaction_type', 'description', 'timestamp', 'status', 'accountnumber', 'accountname', 'reference_number')
    # Or if you're using fieldsets:
    # fieldsets = (
    #     (None, {'fields': ('user', 'amount', 'transaction_type', 'description', 'timestamp', 'status', 'accountnumber', 'accountname', 'reference_number')}),
    # )

admin.site.register(TransactionHistory, TransactionHistoryAdmin)