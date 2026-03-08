from rest_framework.response import Response


def success_response(message, data=None, status_code=200):
    response = {
        "status": True,
        "message": message
    }

    if data:
        response["data"] = data

    return Response(response, status=status_code)


def error_response(message, status_code=400):
    return Response(
        {
            "status": False,
            "message": message
        },
        status=status_code
    )