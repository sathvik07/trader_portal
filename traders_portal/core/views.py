# import logging
# import os
#
# from django.utils.decorators import method_decorator
# from django_ratelimit.decorators import ratelimit
#
#
# logger = logging.getLogger(__name__)
#
# from django.shortcuts import render
# from django.contrib.auth.models import User
#
# from rest_framework import generics, permissions, filters, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
#
# from rest_framework_simplejwt.tokens import RefreshToken
# from firebase_admin import auth as firebase_auth
#
# from . import serializers
# from .models import Company, Watchlist
# from .serializers import (
#     RegisterSerializer,
#     CompanySerializer,
#     WatchlistSerializer
# )
# from .tasks import send_watchlist_email
#
# # -------------------------------
# # User Registration View
# # -------------------------------
# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     permission_classes = [permissions.AllowAny]
#     serializer_class = RegisterSerializer
#
#
# # -------------------------------
# # Firebase Login View
# # -------------------------------
# class FirebaseLoginView(APIView):
#     permission_classes = [permissions.AllowAny]
#
#     def post(self, request):
#         id_token = request.data.get("idToken")
#         if not id_token:
#             return Response({"error": "Missing ID token"}, status=400)
#
#         try:
#             decoded_token = firebase_auth.verify_id_token(id_token)
#             uid = decoded_token["uid"]
#             email = decoded_token.get("email", f"{uid}@firebase.local")
#             name = decoded_token.get("name", email.split("@")[0])
#
#             user, _ = User.objects.get_or_create(
#                 username=uid,
#                 defaults={"email": email, "first_name": name}
#             )
#
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 "access": str(refresh.access_token),
#                 "refresh": str(refresh)
#             })
#
#         except firebase_auth.InvalidIdTokenError:
#             return Response({"error": "Invalid ID token"}, status=401)
#         except Exception as e:
#             return Response({"error": str(e)}, status=500)
#
#
# # -------------------------------
# # Company List View (Searchable)
# # -------------------------------
# class CompanyListView(generics.ListAPIView):
#     queryset = Company.objects.all()
#     serializer_class = CompanySerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['company_name', 'symbol', 'scripcode']
#
#
# # -------------------------------
# # Watchlist Views
# # -------------------------------
# # class WatchlistListCreateView(generics.ListCreateAPIView):
# #     serializer_class = WatchlistSerializer
# #     permission_classes = [permissions.IsAuthenticated]
# #
# #     # @ratelimit(key='user', rate='5/m', block=True)
# #     def post(self, request, *args, **kwargs):
# #         return super().post(request, *args, **kwargs)
# #
# #     def get_queryset(self):
# #         return Watchlist.objects.filter(user=self.request.user)
# #
# #     def perform_create(self, serializer):
# #         user = self.request.user
# #         # company = serializer.validated_data['company']
# #         #
# #         # # Prevent duplicate
# #         # if Watchlist.objects.filter(user=user, company=company).exists():
# #         #     raise serializers.ValidationError("Company already in your watchlist.")
# #         #
# #         # # Create and trigger async task
# #         # watchlist = serializer.save(user=user)
# #         # send_watchlist_email.delay(user.email, company.company_name)
# #         watchlist = serializer.save(user=user)
# #
# #         # Send email (only if the entry was newly created)
# #         if watchlist._state.adding:  # Not a 100% reliable check
# #             send_watchlist_email.delay(user.email, watchlist.company.company_name)
#
#
# class WatchlistListCreateView(generics.ListCreateAPIView):
#     serializer_class = WatchlistSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         return Watchlist.objects.filter(user=self.request.user)
#
#     RATE_LIMIT = os.getenv("RATE_LIMIT", "5/m")
#     @method_decorator(ratelimit(key='user', rate=RATE_LIMIT, method='POST', block=True))
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         user = request.user
#         company = serializer.validated_data['company']
#
#         watchlist, created = Watchlist.objects.get_or_create(user=user, company=company)
#
#         if created:
#             logger.warning("[API] Watchlist created, sending async email...")
#             send_watchlist_email.delay(user.email, company.company_name)
#         else:
#             logger.warning("[API] Watchlist already exists, not sending email.")
#
#         output_serializer = self.get_serializer(watchlist)
#         return Response(output_serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
#
#
#
#
# class WatchlistDeleteView(generics.DestroyAPIView):
#     serializer_class = WatchlistSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = 'pk'
#
#     def get_queryset(self):
#         return Watchlist.objects.filter(user=self.request.user)
#
#



import logging
import os

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import generics, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound

from rest_framework_simplejwt.tokens import RefreshToken
from firebase_admin import auth as firebase_auth

from . import serializers
from .models import Company, Watchlist
from .serializers import (
    RegisterSerializer,
    CompanySerializer,
    WatchlistSerializer
)
from .tasks import send_watchlist_email

logger = logging.getLogger(__name__)
RATE_LIMIT = os.getenv("RATE_LIMIT", "5/m")


# -------------------------------
# User Registration View
# -------------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


# -------------------------------
# Firebase Login View
# -------------------------------
class FirebaseLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        id_token = request.data.get("idToken")
        if not id_token:
            raise ValidationError("Missing ID token")

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            uid = decoded_token["uid"]
            email = decoded_token.get("email", f"{uid}@firebase.local")
            name = decoded_token.get("name", email.split("@")[0])

            user, _ = User.objects.get_or_create(
                username=uid,
                defaults={"email": email, "first_name": name}
            )

            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })

        except firebase_auth.InvalidIdTokenError:
            logger.warning("Invalid Firebase ID token")
            return Response({"error": "Invalid ID token"}, status=401)
        except Exception as e:
            logger.error(f"Firebase login error: {str(e)}")
            return Response({"error": str(e)}, status=500)


# -------------------------------
# Company List View (Searchable)
# -------------------------------
# class CompanyListView(generics.ListAPIView):
#     queryset = Company.objects.all()
#     serializer_class = CompanySerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['company_name', 'symbol', 'scripcode', 'company_id', 'pe', 'roa_ttm']

class CompanyListView(generics.ListAPIView):
    queryset = Company.objects.all().prefetch_related('ttm_ratios')
    serializer_class = CompanySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['company_name', 'symbol', 'scripcode', 'co_code', 'ttm_ratios__pe', 'ttm_ratios__roa_ttm']



# -------------------------------
# Watchlist Views
# -------------------------------
class WatchlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    @method_decorator(ratelimit(key='user', rate=RATE_LIMIT, method='POST', block=True))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        company = serializer.validated_data.get('company')

        if not company:
            raise ValidationError("Company field is required.")

        try:
            watchlist, created = Watchlist.objects.get_or_create(user=user, company=company)

            if created:
                logger.info(f"[Watchlist] Created for user {user.username} - {company}")
                send_watchlist_email.delay(user.email, company.company_name)
            else:
                logger.info(f"[Watchlist] Already exists for user {user.username} - {company}")

            output_serializer = self.get_serializer(watchlist)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except Company.DoesNotExist:
            logger.warning(f"[Watchlist] Company ID not found.")
            raise NotFound("Company not found.")
        except Exception as e:
            logger.error(f"[Watchlist] Unexpected error: {str(e)}")
            raise ValidationError("An unexpected error occurred.")


class WatchlistDeleteView(generics.DestroyAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            logger.info(f"[Watchlist] Deleted item {instance.id} for user {request.user.username}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Watchlist.DoesNotExist:
            logger.warning(f"[Watchlist] Delete failed: item not found.")
            raise NotFound("Watchlist item not found.")
        except Exception as e:
            logger.error(f"[Watchlist] Delete error: {str(e)}")
            raise ValidationError("Failed to delete watchlist item.")





# -------------------------------# Firebase Login View (Django Template)-
from django.views.generic.base import TemplateView

class FirebaseInitialLoginView(TemplateView):
    template_name = 'core/firebase_login.html'
