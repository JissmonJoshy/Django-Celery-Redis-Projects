"""
URL configuration for shop_prj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from shop_app import views
from shop_prj import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.view_login, name='login'),
    path('reviewer_register/', views.reviewer_register, name='reviewer_register'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('reviewer_dashboard/', views.reviewer_dashboard, name='reviewer_dashboard'),

    path('products/', views.product_list, name='product_list'),
    path('products/<int:result_id>/', views.product_detail, name='product_detail'),


    path('api/classifications/', views.api_classification_list, name='api_classification_list'),
    path('api/classifications/<int:pk>/', views.api_classification_detail, name='api_classification_detail'),
    path('api/classifications/<int:pk>/approve/', views.api_classification_approve, name='api_classification_approve'),
    path('api/classifications/<int:pk>/update/', views.api_classification_update, name='api_classification_update'),

    path('import-products/', views.import_products_view, name='import_products'),
    path('run-classification/', views.run_classification_view, name='run_classification'),

]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )