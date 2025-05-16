from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("category/<slug:slug>/", views.category_products_view, name="category_products"),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('myprofile/', views.myprofile, name='myprofile'),
    path('shop/', views.shop, name='shop_products'),
    # path('login/', views.login_view, name='login'),
    path('mycart/myprofile/', views.myprofile, name='my_cart_myprofile'),
    path('mycart/', views.my_cart, name='my_cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),    
    path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path("add-to-wishlist/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("remove_from_wishlist/<int:product_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/<int:item_id>/<int:new_quantity>/', views.update_cart, name='update_cart'),
    path("remove_from_cart/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('myorders/', views.my_orders, name='my_orders'),
    path('myorders/myprofile/', views.myprofile, name='myprofile'),
    path('wishlist/myprofile/', views.myprofile, name='myprofile'),
    path('shop/myprofile/', views.myprofile, name='myprofile'),
    path('category/myprofile/', views.myprofile, name='myprofile'),
    path('myprofile/', views.myprofile, name='myprofile'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('load_states/', views.load_states, name='load_states'),
    # path('update_cart/<int:item_id>/<int:new_quantity>/', views.update_cart, name='update_cart'),
    
    
    # ADMIN Section
    path('dashboard_login/', views.dashboard_login, name='dashboard_login'),
    path('dashboard_panel/', views.dashboard_panel, name='dashboard_panel'),
    path('dashboard_panel/configure_order/', views.configure_order, name='configure_order'),
    path("dashboard_panel/configure_order/orders/delete/<int:order_id>/", views.configure_order, name="delete_order"),
    path("dashboard_panel/configure_order/orders/update/<int:order_id>/", views.configure_order, name="update_order_status"),
    path("dashboard_panel/admin_settings", views.admin_settings, name='admin_settings'),
    path('dashboard_panel/analytics', views.analytics, name='analytics'),
    path('dashboard_panel/productcards/', views.productcards, name='productcards'),
    path('dashboard_panel/category', views.category, name='category'),
    path('dashboard_panel/categories/alter/<int:category_id>/', views.alter_category, name="alter_category"),  # For editing category
    path('dashboard_panel/categories/alter/', views.alter_category, name="alter_category"),  # For adding a category
    path('dashboard_panel/productcardsalter/<int:item_id>/', views.productcardsalter, name='productcardsalter'),
    path('dashboard_panel/productcardsalter/', views.productcardsalter, name='productcardsalter'),  # For adding new items
    path('dashboard_panel/slideshow', views.slideshow, name='slideshow'),
    path('dashboard_panel/slideshow/slideshowalter/<int:item_id>/', views.slideshowalter, name='slideshowalter'),
    path('dashboard_panel/slideshow/slideshowalter/', views.slideshowalter, name='slideshowalter'),
    path('dashboard_panel/comingsoon/', views.comingsoon, name='comingsoon'),
    path('dashboard_panel/comingsoon/altercomingsoon/', views.altercomingsoon, name='altercomingsoon'),
    path('dashboard_panel/view_contact_us/', views.view_contact_us, name='view_contact_us'),
    path('dashboard_panel/view_contact_us/add_country/', views.add_country, name='add_country'),
    path('dashboard_panel/add_country', views.add_country, name='add_country'),
    path('dashboard_panel/alter_country', views.alter_country, name='alter_country'),
    # path('brandoffer', views.brandoffer, name='brandoffer'),
    # path('alterbrandoffer/<int:item_id>/', views.alterbrandoffer, name='alterbrandoffer'),
    # path('alterbrandoffer/', views.alterbrandoffer, name='alterbrandoffer'),  # For adding new items
    
    
    path('dashboard_panel/brand', views.brand, name='brand'),
    path('dashboard_panel/brand/alterbrand/<int:item_id>/', views.alterbrand, name='alterbrand'),
    path('dashboard_panel/brand/alterbrand/', views.alterbrand, name='alterbrand'),
    
    
]