from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from blog.views import RegistrationCreate

handler404 = 'pages.views.page_not_found'

handler500 = 'pages.views.server_error'

urlpatterns = [
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        RegistrationCreate.as_view(),
        name='registration'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     import debug_toolbar

#     urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
