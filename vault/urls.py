from rest_framework_nested import routers

from .views import CollectionViewset, UserViewSet

router = routers.DefaultRouter()

router.register(prefix=r'users', viewset=UserViewSet)

user_router = routers.NestedSimpleRouter(router, parent_prefix='users', lookup='user')
user_router.register(viewset=CollectionViewset, prefix='collections', basename="user-collections")

urlpatterns = router.urls + user_router.urls
