import requests
from drf_yasg.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework import parsers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.parsers import MultipartJsonParser


class BreweriesViewSet(viewsets.ViewSet):
    """
    Example empty viewset demonstrating the standard
    actions that will be handled by a router class.

    If you're using format suffixes, make sure to also include
    the `format=None` keyword argument for each action.
    """

    renderer_classes = [OpenAPIRenderer, SwaggerUIRenderer]
    parser_classes = (MultipartJsonParser, parsers.JSONParser)
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        List Breweries
        Returns a list of breweries.
        https://api.openbrewerydb.org/v1/breweries


            by_dist
            Sort the results by distance from an origin point, denoted by latitude,longitude.

            Run
            ▶
            by_ids
            Comma-separated list of brewery IDs.

            Run
            ▶
            by_name
            Filter breweries by name.

            Note: For the parameters, you can use underscores or url encoding for spaces.

            Run
            ▶
            by_state
            Filter breweries by state.

            Note: Full state name is required; no abbreviations. For the parameters, you can use underscores or url encoding for spaces.

            Run
            ▶
            by_postal
            Filter breweries by postal code.

            May be filtered by basic (5 digit) postal code or more precisely filtered by postal+4 (9 digit) code.

            Note: If filtering by postal+4 the search must include either a hyphen or an underscore.

            Run
            ▶
            by_type
            Filter by type of brewery.

            Must be one of:

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
            Run
            ▶
            page
            The offset or page of breweries to return.

            Run
            ▶
            per_page
            Number of breweries to return each call.

            Note: Default per page 50. Max per page is 200.

            Run
            ▶
            sort
            Sort the results by one or more fields.

            asc for ascending order
            desc for descending order
            Note: by_dist does not work with the sort filter since it is a filter of its own.

            Run
            ▶
        """
        base_url = "https://api.openbrewerydb.org/v1/breweries"
        per_page = 10
        if "per_page" in self.request.query_params:
            per_page = int(self.request.query_params['per_page'])

        base_url += f"/?per_page={per_page}"

        for parameter in ["by_city", "by_dist", "by_ids", "by_name", "by_state", "by_postal", "by_type", "page",
                          "sort"]:
            if parameter in self.request.query_params:
                base_url += f"&{parameter}={self.request.query_params[parameter]}"

        r = requests.get(base_url)
        return Response(r.json())

    def create(self, request):
        pass

    def retrieve(self, request, pk=None):
        """
        Single Brewery
        Get a single brewery.
        https://api.openbrewerydb.org/v1/breweries/{obdb-id}
        """
        base_url = f"https://api.openbrewerydb.org/v1/breweries/{pk}"
        r = requests.get(base_url)
        if r.status_code == 404:
            return Response(r.json(), status=status.HTTP_404_NOT_FOUND
                            )
        return Response(r.json())

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass
