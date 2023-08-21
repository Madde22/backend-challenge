import graphene
from graphene_django import DjangoObjectType

from brewery.models import Brewery
from user.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_active", "is_staff"]


class BreweryType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    breweries = graphene.List(BreweryType)

    def resolve_users(self, info):
        return User.objects.all()

    def resolve_breweries(self, info):
        return Brewery.objects.all()


schema = graphene.Schema(query=Query)
