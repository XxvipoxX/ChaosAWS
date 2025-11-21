from django.contrib import admin
from django.urls import path, include
from main import views as main_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.index, name='index'),
    path('gamepass/', main_views.gamepass, name='gamepass'),
    path('membresias/', main_views.membresias, name='membresias'),
    path('ventajas/', main_views.ventajas, name='ventajas'),
    path('game-session/', main_views.game_session, name='game_session'),
    
    # URLs del carrito y pagos
    path('cart/', main_views.cart, name='cart'),
    path('add-to-cart/', main_views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', main_views.remove_from_cart, name='remove_from_cart'),
    path('payment/', main_views.payment_page, name='payment_page'),
    path('payment/process/', main_views.process_payment, name='process_payment'),
    path('payment/success/<int:order_id>/', main_views.payment_success, name='payment_success'),
    path('payment/cancel/', main_views.payment_cancel, name='payment_cancel'),
    
    path('accounts/', include('accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)