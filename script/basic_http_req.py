import requests
import argparse
import json

class RequestPersist:
    def __init__(self):
        self.user_conf = {   ### optional saved args
            'payload' : {},
            'session' : None,
            'auth' : None
        }
        self.latest_request = None

    ### # should probably be moved to a separate class, or tacked onto argparse ####### ###
        self.parser = argparse.ArgumentParser(description='process program inputs')
        self.__process_args()
    def __valid_host(self,value):
        if str(value):  ##tbd
            return value
    def __valid_port(self,value):
        if not (0 < float(value) < 65535):
            raise argparse.ArgumentError(None, "port must be between 0 and 65535")
        else:
            return value
    def __valid_route(self,value):
        if str(value):  ##tbd
            return value
    def __process_args(self):
        self.parser.add_argument('-ms','--message',type=self.__valid_host, required=True)
        self.parser.add_argument('-ho','--host',  type=self.__valid_host,  required=True)
        self.parser.add_argument('-po','--port',  type=self.__valid_port,  required=False)
        self.parser.add_argument('-ro','--route', type=self.__valid_route, required=False)
        for key, value in vars(self.parser.parse_args()).items():
            self.user_conf[key] = value
    ### ############################################################################### ###

    def __update_payload(self):
        tmpHash = {}
        while True:
            tmpKey = input("key: ")
            tmpValue = input("value: ")
            tmpHash[tmpKey] = tmpValue
            if (input("continue? [y/n] ").lower() == 'n'):
                return dict(tmpHash)

    def __update_conf(self):
        newKey = input("conf key: ")
        newData = self.__update_payload() if newKey == 'payload' else input("conf value: ")
        partial = [s for s in self.user_conf if s.startswith(str(newKey))]
        partial = partial[0] if partial else 0            ### match first case, not great
        if (partial and not ( newKey in self.user_conf)):
            if (input("provided key has a partial match with %s, do you want to overwrite? [y/n]  " % partial).lower() == "y"):
                self.user_conf[str(partial)] = newData
                return     ### end on success, else end on default
        self.user_conf[newKey] = newData

    def __specific_auth(self):  ### try and set auth header value if none
        if self.latest_request:
            responseText = json.loads(self.latest_request.text)
        else:
            return
        if responseText['token']:     ### token is a known example, set case by case
            self.user_conf['auth'] = "Bearer " + responseText['token']

    ### user input
    def get_user_input(self):
        if not self.user_conf['session'] or not (input('maintain session? [y/n]  ') == 'y'):
            self.user_conf['session'] = requests.session()
        elif not (self.user_conf['auth']):
            self.__specific_auth()

        while True:
            print("current parameters:\n" + str(self.user_conf))
            if (input("update parameters? [y/n] ").lower() == 'n'):
                return
            self.__update_conf()

    def make_request(self):
        custom_url = str(self.user_conf['host'])
        custom_url += (":" + str(self.user_conf['port'])) if self.user_conf['port'] else ""
        custom_url += (str(self.user_conf['route'])) if self.user_conf['route'] else ""

        custom_headers = {
            'Authorization' : (self.user_conf['auth'] if self.user_conf['auth'] else "")
        }

        try: #catch 'requests' error response exception
            if str(self.user_conf['message']) == 'POST':
                custom_headers['Content-type'] = 'application/json'
                self.latest_request = self.user_conf['session'].post(
                    custom_url,
                    headers=dict(custom_headers),
                    data=json.dumps(self.user_conf['payload']))
            elif str(self.user_conf['message']) == 'GET':
                self.latest_request = self.user_conf['session'].get(
                    custom_url,
                    params=self.user_conf['payload'],
                    headers=dict(custom_headers),
                    )
            print("request responded with content:\n " + str(self.latest_request.text))
            print("request responded with status:\n    " + str(self.latest_request.status_code))
        except Exception as e:
            print ("ERRORED WITH:\n" + str(e))

user_request = RequestPersist()

while True:
    user_request.get_user_input()
    user_request.make_request()
    if input("Set up new request? [y/n] ").lower() == 'n':
        break