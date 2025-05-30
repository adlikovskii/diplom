from django.urls import path

from . import views

app_name = "backend"

urlpatterns = [
    path("upload/", views.UploadProductsView.as_view(), name="upload"),
    path("products/", views.ListProductView.as_view(), name="products"),
    path(
        "add_order_items/",
        views.AddOrderItemView.as_view(),
        name="add_order_items",
    ),
    path("basket", views.ListItemsOrder.as_view(), name="basket"),
    path("order/<int:pk>/", views.DetailOrderView.as_view(), name="order"),
    path(
        "delete_order_item/<int:pk>/",
        views.DeleteOrderItemView.as_view(),
        name="delete_order_item",
    ),
    path("orders/", views.ListOrderView.as_view(), name="orders"),
    path(
        "confirm/<int:id>/", views.ConfirmOrderView.as_view(), name="confirm"
    ),
]
