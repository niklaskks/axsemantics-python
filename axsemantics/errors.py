class AXSemanticsError(Exception):

    def __init__(self, message=None, request=None):
        super(AXSemanticsError, self).__init__(message)
        self.request = request


class APIConnectionError(AXSemanticsError):
    def __str__(self):
        if self.request:
            return 'Could not connect to {}.'.format(
                self.request.request.url,
            )
        
        return self._message or '<no further information'


class APIError(AXSemanticsError):
    def __str__(self):
        if self.request:
            return 'Got status code {} in answer to a {} request to {}.'.format(
                self.request.status_code,
                self.request.request.method,
                self.request.request.url,
            )
        
        return self._message or '<no further information'
