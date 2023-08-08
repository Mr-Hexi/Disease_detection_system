"""Disease_Detection_System URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from home import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # Include the home.urls for the root path
    # path('braintumor/', include('home.urls')), 
    # path('pneumonia/', include('home.urls')),
    # path('retinal/', include('home.urls')),
    # path('btpred/', include('home.urls')),
    # path('pnapred/', include('home.urls')),
    # path('retpred/', include('home.urls')),
    # path('login/', include('home.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Only for development purpose
urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# from django.contrib import admin
# from django.urls import path, include
# from django.conf.urls.static import static
# from django.conf import settings

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('home.urls')),  
#     # path('accounts/', include("django.contri.auth.urls")),  
# ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# # Only for development purpose
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

