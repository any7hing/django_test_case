from django_filters import FilterSet, DateFromToRangeFilter
from news.models import News


class NewsFilter(FilterSet):
    
    created_at = DateFromToRangeFilter()
    class Meta:
        
        model = News
        fields = ["autor",'created_at', 'status', 'like',]

