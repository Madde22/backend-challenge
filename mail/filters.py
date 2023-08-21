import django_filters
from django_filters import DateFilter, CharFilter, NumberFilter

from mail.models import Mail


class MailFilter(django_filters.FilterSet):
    vendor = NumberFilter(field_name='vendor')
    customer = NumberFilter(field_name='customer')

    store_name = CharFilter(field_name='vendor__store_name', lookup_expr='icontains')
    vendor_email = CharFilter(field_name='vendor__user__email', lookup_expr='icontains')
    customer_email = CharFilter(field_name='customer__email', lookup_expr='icontains')
    order_num = CharFilter(field_name='order_num', lookup_expr='icontains')
    type = CharFilter(field_name='type', lookup_expr='icontains')
    title = CharFilter(field_name='title', lookup_expr='icontains')
    bcc = CharFilter(field_name='bcc', lookup_expr='icontains')
    cc = CharFilter(field_name='cc', lookup_expr='icontains')
    from_email = CharFilter(field_name='from_email', lookup_expr='icontains')
    from_user = CharFilter(field_name='from_user', lookup_expr='icontains')

    from_date = DateFilter(field_name='created_at', lookup_expr='gte')
    to_date = DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Mail
        fields = []
