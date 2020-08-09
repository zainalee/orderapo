from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
# from useradmin.views import adminstrator

urlpatterns = [
    path('', views.home, name='home'),
    path('demo', views.demo, name='demo'),
    path('shop', views.shop, name='shop'),
    path('profile', views.profile, name='profile'),
    path('profile/<str:pk>', views.showprofile, name='profile'),
    path('login', views.login, name='login'),
    path('Clientlogin', views.Clientlogin, name='Clientlogin'),
    path('logout', views.logoutuser, name='logout'),
    path('products', views.products, name='products'),
    path('createproduct/', views.createproduct, name='createproduct'),
    path('updateproduct/<str:pk>', views.updateproduct, name='updateproduct'),
    path('deleteproduct/<str:pk>', views.deleteproduct, name='deleteproduct'),
    path('registration', views.registration, name='registration'),
    path('Clientregistration', views.ClientRegistration, name='cregister'),
    path('cart', views.cart, name='cart'),
    path('update_item', views.updateItem, name='update_item'),
    path('process_order', views.processOrder, name='process_order'),
    path('checkout', views.checkout, name="checkout"),
    path('main', views.main, name='main'),
    path('detailview/<str:pk>', views.detailview, name='detailview'),
    path('myOrders', views.myOrders, name='myorders'),
    path('selling', views.selling, name='selling'),
    path('adminhome', views.adminhome, name='adminhome'),
    # path('adminstrator', views.adminstrator, name='adminstrator')

    # password-reset
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),
         name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_sent.html'),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_form.html'),
         name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'),
         name="password_reset_complete"),


]
