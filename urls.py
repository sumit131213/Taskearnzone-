from django.contrib import admin
from django.urls import path
from earning.views import dashboard, register_view, login_view, logout_view, withdraw_view, privacy_policy, ad_network_postback, monlix_postback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('withdraw/', withdraw_view, name='withdraw'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'), 
    
    # Automatic ad network postback system ka link
    path('api/postback/', ad_network_postback, name='ad_network_postback'),
    path('api/monlix-postback/', monlix_postback, name='monlix_postback'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)