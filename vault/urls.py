from django.urls import path
from rest_framework_nested import routers

from .views import CollectionViewset, UserViewset, PrivateFileViewset, AccessLogViewset, FilePermissionViewset, FileShareViewset

router = routers.DefaultRouter()

router.register(prefix='users', viewset=UserViewset, basename='users')
router.register(prefix='files', viewset=PrivateFileViewset, basename='files')
router.register(prefix='fileshare', viewset=FileShareViewset, basename='fileshare')

user_router = routers.NestedDefaultRouter(router, parent_prefix='users', lookup='user')
user_router.register(prefix='collections', viewset=CollectionViewset, basename="user-collections")

file_router = routers.NestedDefaultRouter(router, parent_prefix='files', lookup='file')
file_router.register(prefix='logs', viewset=AccessLogViewset, basename="file-logs")

custom_permission_url = [
    path('files/<int:file_pk>/permission/', FilePermissionViewset.as_view({'get': 'retrieve', 'patch': 'update'}),
         name='file-permission'),
]
urlpatterns = router.urls + user_router.urls + file_router.urls + custom_permission_url
