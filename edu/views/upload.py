from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request


@api_view(['POST', 'PUT'])
def upload(request: Request):
    return Response({
        'message': 'you have used upload endpoint',
    }, status.HTTP_200_OK)
