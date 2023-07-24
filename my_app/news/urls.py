from rest_framework.routers import DefaultRouter
from news.views import NewsViewSet

router = DefaultRouter()
router.register('news', NewsViewSet)
urlpatterns = router.urls