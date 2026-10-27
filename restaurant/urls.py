from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('bookings', views.BookingViewSet, basename='booking')

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('book/', views.book, name="book"),
    path('reservations/', views.reservations, name="reservations"),
    path('menu/', views.menu, name="menu"),
    path('menu_item/<int:pk>/', views.display_menu_item, name="menu_item"),
    path('bookings', views.bookings, name='bookings'),
    path('api/menu-items/', views.MenuItemsView.as_view(), name='menu-items'),
    path('api/menu-items/<int:pk>/', views.SingleMenuItemView.as_view(), name='menu-item-detail'),
    path('api/', include(router.urls)),
]
