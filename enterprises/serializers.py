from rest_framework import serializers

from enterprises.models import Company, CarService


class EnterpriseSerializer(serializers.HyperlinkedModelSerializer):
    added_by = serializers.ReadOnlyField(source='added_by.username')
    is_verified = serializers.ReadOnlyField()


class CompanySerializer(EnterpriseSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='company-detail', lookup_field='slug'
    )

    class Meta:
        model = Company
        fields = '__all__'


class CarServiceSerializer(EnterpriseSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='service-detail', lookup_field='slug'
    )
    company = serializers.SlugRelatedField(
        slug_field='name', queryset=Company.objects.all()
    )

    class Meta:
        model = CarService
        fields = '__all__'
