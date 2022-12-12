class RequestError:
    malformed_request = {"status": 400, "error": "MALFORMED_REQUEST"}
    unauthorized = {"status": 401, "error": "UNAUTHORIZED"}
    forbidden = {"status": 403, "error": "FORBIDDEN"}
    not_found = {"status": 404, "error": "CONTENT_NOT_FOUND"}
    server_error = {"status": 500, "error": "INTERNAL_SERVER_ERROR"}
    corrupt = {"status": 500, "error": "CORRUPT_DATA"}
    service_unavailable = {"status": 503, "error": "SERVICE_UNAVILABLE"}
    conflict = {
        "status": 409,
        "error": "CONFLICT",
        "message": "The request has been cancelled",
    }

    expired_signature = {"status": 401, "error": "EXPIRED SIGNATURE"}
    invalid_signature = {"status": 401, "error": "INVALID_SIGNATURE"}
    invalid_token = {"status": 401, "error": "INVALID_TOKEN"}

    not_authenticated = {"status": 401, "error": "NO_AUTH"}
    no_cookie = {"status": 401, "error": "NO_AUTHCOOKIE"}
    expired_cookie = {"status": 401, "error": "EXPIRED_AUTHCOOKIE"}

    failed_login = {"status": 400, "error": "FAILED_LOGIN"}


# class PintaError(RequestError):
#     invalid_name = 'INVALID_NAME'
#     duplicate_name = 'DUPLICATE_NAME'
#     invalid_parent = 'INVALID_PARENT'
#     circular_dependency = 'CIRCULAR_DEPENDENCY'
#     invalid_links = 'INVALID_LINKS'
#     invalid_tags = 'INVALID_TAGS'
#     invalid_id = 'INVALID_ID'

#     parent_not_found = 'PARENT_NOT_FOUND'
#     bucket_not_found = 'BUCKET_NOT_FOUND'
#     directory_not_found = 'DIRECTORY_NOT_FOUND'
#     file_not_found = 'FILE_NOT_FOUND'

#     invalid_date = 'INVALID_DATE'
#     invalid_attribute = 'INVALID_ATTRIBUTE'


# class WebSocketError(RequestError):
#     invalid_event = 'INVALID_EVENT'
#     invalid_id = 'INVALID_ID'
#     invalid_date = 'INVALID_DATE'
#     invalid_attribute = 'INVALID_ATTRIBUTE'
#     invalid_check_type = 'INVALID_CHECK_TYPE'
#     invalid_check_attribute = "INVALID_CHECK_ATTRIBUTE"
