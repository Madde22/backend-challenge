import uuid

from django.db import models

from utils.constants import MICRO, NANO, REGIONAL, LARGE, BREWPUB, PLANNING, BAR, CONTRACT, PROPRIETOR, CLOSED

"""
micro - Most craft breweries. For example, Samual Adams is still considered a micro brewery.
nano - An extremely small brewery which typically only distributes locally.
regional - A regional location of an expanded brewery. Ex. Sierra Nevada’s Asheville, NC location.
brewpub - A beer-focused restaurant or restaurant/bar with a brewery on-premise.
large - A very large brewery. Likely not for visitors. Ex. Miller-Coors. (deprecated)
planning - A brewery in planning or not yet opened to the public.
bar - A bar. No brewery equipment on premise. (deprecated)
contract - A brewery that uses another brewery’s equipment.
proprietor - Similar to contract brewing but refers more to a brewery incubator.
closed - A location which has been closed.
"""


class Brewery(models.Model):
    BREWERY_TYPE = (
        (MICRO, "micro"),
        (NANO, "nano"),
        (REGIONAL, "regional"),
        (BREWPUB, "brewpub"),
        (LARGE, "large"),
        (PLANNING, "planning"),
        (BAR, "bar"),
        (CONTRACT, "contract"),
        (PROPRIETOR, "proprietor"),
        (CLOSED, "closed"),
    )
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    brewery_type = models.CharField(max_length=20, blank=True, null=True, choices=BREWERY_TYPE)
    address_1 = models.CharField(max_length=255, blank=True, null=True)
    address_2 = models.CharField(max_length=255, blank=True, null=True)
    address_3 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state_province = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=255, blank=True, null=True)
    website_url = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
