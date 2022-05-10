class NotionAccessDenied(Exception):
    pass


class TokenRequestFailed(Exception):
    def __init__(self, request_data: dict, response_status: int, response_body: str):
        self.request_data = request_data
        self.response_status = response_status
        self.response_body = response_body
