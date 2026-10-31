
from django.utils.deprecation import MiddlewareMixin

class AddPartitionedAttributeMiddleware(MiddlewareMixin):
    def process_response(self, request, response):

        if "sessionid" in response.cookies:
            response.cookies["sessionid"]["samesite"] = "Lax"
            response.cookies["sessionid"]["secure"] = False

        if "csrftoken" in response.cookies:
            response.cookies["csrftoken"]["samesite"] = "Lax"
            response.cookies["csrftoken"]["secure"] = False

        return response
