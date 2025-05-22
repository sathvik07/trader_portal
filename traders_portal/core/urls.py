from django.urls import path
from .views import RegisterView, FirebaseLoginView, CompanyListView, WatchlistListCreateView, WatchlistDeleteView, FirebaseInitialLoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('firebase-login/', FirebaseLoginView.as_view(), name='firebase_login'),
    path('companies/', CompanyListView.as_view(), name='company-list'),
    path('watchlist/', WatchlistListCreateView.as_view(), name='watchlist'),
    path('watchlist/<int:pk>/', WatchlistDeleteView.as_view(), name='watchlist-delete'),
    path('firebase-login-page/', FirebaseInitialLoginView.as_view(), name='firebase-login-page'),

]
