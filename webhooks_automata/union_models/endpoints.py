import abc
import hashlib
import hmac
from typing import Literal, TYPE_CHECKING
from pydantic import BaseModel, SecretStr

if TYPE_CHECKING:
    import starlette.requests

all_endpoints = list()


class EndpointBase(BaseModel, abc.ABC):
    suffix: str

    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__(**kwargs)
        all_endpoints.append(cls)
    
    @abc.abstractmethod
    async def authorize(self, request: "starlette.requests.Request") -> bool:
        pass


class PlainEndpoint(EndpointBase):
    provider: Literal["plain"]

    async def authorize(self, request):
        return True


class GitHubEndpoint(EndpointBase):
    provider: Literal["github"]
    secret_token: SecretStr

    def verify_signature(self, payload_body, signature_header):
        """Verify that the payload was sent from GitHub by validating SHA256.
        
        Raise and return 403 if not authorized.

        This function was mostly reused from the official GitHub documentation:
        https://docs.github.com/en/webhooks-and-events/webhooks/securing-your-webhooks
        
        Args:
            payload_body: original request body to verify (request.body())
            secret_token: GitHub app webhook token (WEBHOOK_SECRET)
            signature_header: header received from GitHub (x-hub-signature-256)
        """
        if not signature_header:
            print("x-hub-signature-256 header is missing!")
            return False
        
        hash_object = hmac.new(self.secret_token.get_secret_value().encode('utf-8'), 
                               msg=payload_body, digestmod=hashlib.sha256)
        expected_signature = "sha256=" + hash_object.hexdigest()
        if not hmac.compare_digest(expected_signature, signature_header):
            print("Request signatures didn't match!")
            print("Expected: %s" % expected_signature)
            print("Header: %s" % signature_header)
            print("Body:\n%s" % payload_body)
            return False
        
        return True

    async def authorize(self, request):
        return self.verify_signature(await request.body(), request.headers.get("x-hub-signature-256"))


class GitlabEndpoint(EndpointBase):
    provider: Literal["gitlab"]
    secret_token: SecretStr

    async def authorize(self, request):
        if request.headers.get("x-gitlab-token") == self.secret_token.get_secret_value():
            return True
        else:
            return False
