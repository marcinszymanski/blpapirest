from utils import RefDataResponseParser
import blpapi
import uuid
from datetime import date, timedelta

class RefDataSvc:
    
    def __init__(self, host, port):
        self.parser = RefDataResponseParser()
        
        self.sessionOptions = blpapi.SessionOptions()
        self.sessionOptions.setServerHost(host)
        self.sessionOptions.setServerPort(port)
        self.connected = False
    
        self.session = blpapi.Session(self.sessionOptions)
        if not self.session.start():
            print "Failed to connect!"
            return
            
        if not self.session.openService("//blp/refdata"):
            self.session.stop()
            print "Failed to open //blp/refdata"
            return
        
        self.refDataService = self.session.getService("//blp/refdata")
        self.connected = True
        
    def __del__(self):
        self.session.stop
        
    def _buildRequestBase(self, requestType, ticker, fields):
        request = self.refDataService.createRequest(requestType)
        request.append("securities", ticker)
        for field in fields:
            request.append("fields", field)
        return request
    
    def _sendRequest(self, request):
        cid = blpapi.CorrelationId(uuid.uuid4())
        print "Sending Request:", request
        self.session.sendRequest(request, correlationId=cid)

    def _handleResposes(self, cid):
        result = {}
        try:
            tempResult = {"securitiesData": []}
            while(True):
                event = self.session.nextEvent(500)
                for msg in event:
                    if event.eventType() == blpapi.Event.RESPONSE or event.eventType() == blpapi.Event.PARTIAL_RESPONSE:
                        self.parser.parseMessage(msg, tempResult["securitiesData"])
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            result = tempResult;
        finally:
            return result 
    
 
    def getReferenceData(self, ticker, fields):
        if self.connected == False:
            return {"error" : "Service not connected"}
        
        request = self._buildRequestBase("ReferenceDataRequest", ticker, fields)
        cid = self._sendRequest(request)

        return self._handleResposes(cid)

        
    def getHistoricalData(self, ticker, fields, startDate = str(date.today() - timedelta(days=31)).replace("-",""), endDate = str(date.today()).replace("-",""), periodicity = "DAILY", maxPoints = 100):
        if self.connected == False:
            return {"error" : "Service not connected"}
    
        request = self._buildRequestBase("HistoricalDataRequest", ticker, fields)
        
        request.set("periodicitySelection", periodicity)
        request.set("startDate", startDate)
        request.set("endDate", endDate)
        request.set("maxDataPoints", maxPoints)

        cid = self._sendRequest(request)

        return self._handleResposes(cid)

  