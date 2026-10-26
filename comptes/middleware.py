from django.utils.deprecation import MiddlewareMixin

class AddPartitionedAttributeMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Modifier les cookies de session
        if "sessionid" in response.cookies:
            response.cookies["sessionid"]["samesite"] = "None"
            response.cookies["sessionid"]["secure"] = True
        
        # Modifier les cookies CSRF
        if "csrftoken" in response.cookies:
            response.cookies["csrftoken"]["samesite"] = "None"
            response.cookies["csrftoken"]["secure"] = True
        
        return response
