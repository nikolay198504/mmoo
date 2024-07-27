from .models import Comment, Bill
from django_filters import FilterSet, ModelChoiceFilter


class BillFilter(FilterSet):
    class Meta:
        model = Comment
        fields = ['comment_bill']

    def __init__(self, *args, **kwargs):
        super(BillFilter, self).__init__(*args, **kwargs)
        self.filters['comment_bill'].queryset = Bill.objects.filter(author_id=kwargs['request'])
