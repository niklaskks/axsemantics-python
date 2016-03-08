class AXSemanticsError(Exception):

    def __init__(self, request=None, message=None):
        super(AXSemanticsError, self).__init__(message)
        self.request = request
        self.message = message


class APIConnectionError(AXSemanticsError):
    def __str__(self):
        if self.request:
            return 'Could not connect to {}.'.format(
                self.request.request.url,
            )

        return self.message or '<no further information'


class APIError(AXSemanticsError):
    def __str__(self):
        if self.request:
            return 'Got status code {} in answer to a {} request to {}.'.format(
                self.request.status_code,
                self.request.request.method,
                self.request.request.url,
            )

        return self.message or '<no further information>'


class AuthenticationError(AXSemanticsError):
    def __str__(self):
        if self.request:
            return 'Failed to authenticate against {}.'.format(
                self.request.request.url
            )

        return self.message or 'Failed to authenticate.'
