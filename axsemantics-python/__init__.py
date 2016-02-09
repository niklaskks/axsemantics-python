# AX-Semantics Python bindings
# API docs at https://apidocs.ax-semantics.com


# Configuration
api_key = None
api_base = 'https://my.ax-semantics.com/api'
api_version = 'v1'


from axsemantics.resource import (
    ContentProject,
    Thing,
)


from axsemantics.error import (
    APIConnectionError,
    AuthenticationError,
    AXSemanticsError,
    InvalidRequestError,
)
