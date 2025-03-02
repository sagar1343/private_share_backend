from rest_framework_nested import routers

from .views import CollectionViewset, UserViewset, PrivateFileViewset, AccessLogViewset, FilePermissionViewset

router = routers.DefaultRouter()

router.register(prefix='users', viewset=UserViewset, basename='users')
router.register(prefix='files', viewset=PrivateFileViewset, basename='files')

user_router = routers.NestedDefaultRouter(router, parent_prefix='users', lookup='user')
user_router.register(prefix='collections', viewset=CollectionViewset, basename="user-collections")

file_router = routers.NestedDefaultRouter(router, parent_prefix='files', lookup='file')

file_router.register(prefix='logs', viewset=AccessLogViewset, basename="file-logs")
router.register(prefix='file-permissions', viewset=FilePermissionViewset)
urlpatterns = router.urls + user_router.urls + file_router.urls
