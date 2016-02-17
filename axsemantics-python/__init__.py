# AX-Semantics Python bindings
# API docs at https://apidocs.ax-semantics.com


# Configuration
API_TOKEN = None
API_BASE = 'https://api.ax-semantics.com'
API_VERSION = 'v1'


from axsemantics.axresource import (
    ContentProject,
    Thing,
)


from axsemantics.error import (
    APIConnectionError,
    AuthenticationError,
    AXSemanticsError,
    InvalidRequestError,
)
