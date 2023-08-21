import graphene
from graphene_django import DjangoObjectType

from brewery.models import Brewery
from graphene import relay


class BreweryType(DjangoObjectType):
    class Meta:
        model = Brewery
        fields = ["id", "name", "brewery_type",  "address_1", "address_2", "address_3",
                  "city", "state_province", "postal_code", "country",  "latitude",
                  "longitude", "phone", "website_url", "state", "street"]
        interfaces = (relay.Node,)
        filter_fields = ['name', 'genus', 'is_domesticated']


class Query(graphene.ObjectType):
    breweries = graphene.List(BreweryType)

    def resolve_breweries(self, info):
        return Brewery.objects.all()


schema = graphene.Schema(query=Query)
