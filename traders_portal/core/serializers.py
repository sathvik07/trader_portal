from rest_framework import serializers
from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user




# core/serializers.py
from rest_framework import serializers
from .models import Company, Watchlist

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class WatchlistSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        source='company',
        write_only=True
    )

    class Meta:
        model = Watchlist
        fields = ['id', 'company', 'company_id']

    def create(self, validated_data):
        user = self.context['request'].user
        company = validated_data['company']
        # This will return the existing one if already present, or create a new one
        watchlist_item, created = Watchlist.objects.get_or_create(user=user, company=company)
        return watchlist_item
