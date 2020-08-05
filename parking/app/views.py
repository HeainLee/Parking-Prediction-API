from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

class ParkingModelView(APIView):
    def get(self, request):
        # queryset = Algorithm.objects.all().order_by('id')
        # serializer = ALGOSerializer(queryset, many=True)
        return Response("ParkingModelView", status=status.HTTP_200_OK)
