
class RefDataResponseParser:

    def parseMessage(self, msg, result):
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
                fieldData = {}
                self._parseFieldData(securityData.getElement("fieldData").getValue(i), fieldData)
                fieldsData.append(fieldData)
        else:
            fieldData = {}
            self._parseFieldData(securityData.getElement("fieldData"), fieldData)
            fieldsData.append(fieldData)
            
        data["fieldsData"] = fieldsData
        
        resultSecuritiesData.append(data)
        print data
        
    def _parseFieldData(self, fieldData, resultFieldData):        
        for i in range(fieldData.numElements()):
            resultFieldData[str(fieldData.getElement(i).name())] = fieldData.getElementAsString(fieldData.getElement(i).name())