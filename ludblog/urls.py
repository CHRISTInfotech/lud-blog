from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog.views import *


from django.conf.urls import handler404, handler500, handler403, handler400
from django.shortcuts import render

# Custom error views (Global for all apps)
def custom_404(request, exception):
    return render(request, "errors/404.html", status=404)

def custom_500(request):
    return render(request, "errors/500.html", status=500)

def custom_403(request, exception):
    return render(request, "errors/403.html", status=403)

def custom_400(request, exception):
    return render(request, "errors/400.html", status=400)

def custom_503(request, exception):
    return render(request, "errors/503.html", status=503)

# Assign error handlers globally
handler404 = "ludblog.urls.custom_404"
handler500 = "ludblog.urls.custom_500"
handler403 = "ludblog.urls.custom_403"
handler400 = "ludblog.urls.custom_400"
handler503 = "ludblog.urls.custom_503"



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('users/', include('users.urls')),
    path('cadmin/',include('cadmin.urls')),
    path('api/recent-blogs/', RecentBlogsAPI.as_view(), name='recent_blogs'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)

# Allow serving media files when ALLOW_MEDIA is True
if settings.ALLOW_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)