from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from blpapirest import refdatasvc

refDataSvc = refdatasvc.RefDataSvc('10.8.8.1', 8194)

class RefDataSvcView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class RefDataView(RefDataSvcView):
    def get(self, request, format=None):
        return Response(refDataSvc.getReferenceData(request.QUERY_PARAMS['ticker'], request.QUERY_PARAMS['field'].split(',')))   
     
class HistDataView(RefDataSvcView):
    def get(self, request, format=None):
        return Response(refDataSvc.getHistoricalData(request.QUERY_PARAMS['ticker'], request.QUERY_PARAMS['field'].split(',')))   
