import requests, json, sys

class Test:
    def __init__(self, test_file):
        with open(test_file) as f:
            self.config = json.loads(f.read())
        self.server = self.config["server"]

    def _check_body(self, response_draft, response_real):
        response = json.loads(response_real)
        for key, value in response_draft.items():
            if key not in response:
                print "invalid key "+key+" test failed!" 
                sys.exit()
            if "var_type" in value:
                if type(response[key]).__name__ != value["var_type"]:
                    print "invalid type "+value["var_type"]+" for key "+key + ", found type: "+type(response[key]).__name__+" test failed!" 
                    sys.exit()
            else:
                if type(response[key]) is dict:
                    self._check_body(value, json.dumps(response[key]))
                elif type(response[key]) is list:
                    self._check_body(value[0], json.dumps(response[key][0]))
                
    
    def _check_status(self, res, test):
        if res.status_code in test["status_permitted"]:
            return res.text
        else:
            print "invalid status code returned ("+str(res.status_code)+"), test failed!"
            sys.exit()
    
    def _get(self,test):
        res = requests.get(self.server + test["endpoint"])
        self._check_status(res, test)
        self._check_body(test["response_draft"], res.text)

    def _post(self,test):
        res = requests.post(self.server + test["endpoint"], test["body"])
        self._check_status(res, test)
        self._check_body(test["response_draft"], res.text)

    def _method_not_found(self, test):
        print "Method "+test["method"]+" is invalid"

    def run(self):
        for group_name, group in self.config.items():
            if type(group) is dict:
                print "Testing " + group["description"] + "..."
                for test_name, test in group.items():
                    if type(test) is dict:
                        print "Doing test " + test["description"] + "..."
                        getattr(self, '_'+test["method"].lower(), None)(test)
                        print "Test "+test["description"]+" sucessfull"
