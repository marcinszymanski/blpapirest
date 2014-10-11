import blpapi
import uuid

from datetime import date, timedelta

class RefDataSvc:
    
    def __init__(self, host, port):
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
                        self._parseMessage(msg, tempResult["securitiesData"])
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
            result = tempResult;
        finally:
            return result#{  "securitiesData": [    {"ticker": "IBM US Corp", "fields" : [      {"name": "PX_LAST", "value" : "185.930000"},      {"name": "DS002", "value" : "INTL BUSINESS MACHINES CORP"}     ]    }  ]} 
    
    def _parseMessage(self, msg, result):
        print msg
        if msg.getElement("securityData").isArray():            
            for i in range(msg.getElement("securityData").numValues()):
                self._parseSecurityData(msg.getElement("securityData").getValue(i), result)
        else:
            self._parseSecurityData(msg.getElement("securityData"), result)
    
    def _parseSecurityData(self, securityData, resultSecuritiesData):
        data = {}
        if not securityData.hasElement("security"):
            return
        data["security"] = securityData.getElementAsString("security")
        if not securityData.hasElement("fieldData"):
            return
        
        fieldsData = []
        if securityData.getElement("fieldData").isArray():
            for i in range(securityData.getElement("fieldData").numValues()):
                self._parseFieldData(securityData.getElement("fieldData").getValue(i), fieldsData)
        else:
            self._parseFieldData(securityData.getElement("fieldData"), fieldsData)
            
        data["fieldsData"] = fieldsData
        
        resultSecuritiesData.append(data)
        print data
        
    def _parseFieldData(self, fieldData, resultFieldsData):
        print fieldData.numElements()
        for i in range(fieldData.numElements()):
            resultFieldsData.append({"name" : str(fieldData.getElement(i).name()),
                                     "value" : fieldData.getElementAsString(fieldData.getElement(i).name())
                                    })
 
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

  