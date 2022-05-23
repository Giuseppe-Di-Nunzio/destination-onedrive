#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Mapping, Any, Iterable

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, ConfiguredAirbyteCatalog, AirbyteMessage, Status, Type
import os, csv, json, requests, msal


class DestinationOnedrive(Destination):
    base_file = "/tmp/"
    def write(
            self,
            config: Mapping[str, Any],
            configured_catalog: ConfiguredAirbyteCatalog,
            input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:

        """
        TODO
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """
        result = None
        body_json = []

        # Firstly, check the cache to see if this end user has signed in before
        app = msal.PublicClientApplication(config["client_id"], authority=config["authority"],  )
        accounts = app.get_accounts(username=config["username"])
        if accounts:
             # logging.info("Account(s) exists in cache, probably with token too. Let's try.")
             result = app.acquire_token_silent(config["scope"], account=accounts[0])        
        
        if not result:
             result = app.acquire_token_by_username_password(config["username"], config["password"], scopes=["Files.ReadWrite"] ) 

        if "access_token" in result:
             try:
                 message = next(input_messages)
                 #print (message.record.stream)
                 if message.type == Type.STATE:
                     yield message
                 elif  message.type == Type.RECORD:
                          old_stream = message.record.stream
                          body_json.append(message.record.data)
                          while True:
                                   try:
                                        message = next(input_messages)
                                        #print (message.record.stream)
                                        if message.type == Type.STATE:
                                              yield message
                                        elif  (message.type == Type.RECORD) :
                                              if old_stream == message.record.stream:
                                                  body_json.append(message.record.data)
                                              else:
                                                  self._create_temporary_file (self.base_file+old_stream+'.csv', body_json )
                                                  # this is where upload really happen
                                                  content = open(self.base_file+old_stream+'.csv','rb')
                                                  response = json.loads(requests.put('https://graph.microsoft.com/v1.0/me/drive/root:/'+config["folder"]+'/'+old_stream+'.csv:/content',headers={'Authorization': 'Bearer ' + result['access_token']} , data = content ).text )
                                                  print ("risposta ricevuta %s " % response)
                                                  # delete temporary file when upload is completed
                                                  self._remove_temporary_file (self.base_file+old_stream+'.csv')
                                                  # let's move on
                                                  old_stream = message.record.stream
                                                  body_json.clear()
                                                  body_json.append(message.record.data)
                                   except StopIteration:
                                     #print ('end of streams.')
                                     self._create_temporary_file (self.base_file+old_stream+'.csv', body_json )
                                     # this is where upload really happen
                                     content = open(self.base_file+old_stream+'.csv','rb')
                                     response = json.loads(requests.put('https://graph.microsoft.com/v1.0/me/drive/root:/'+config["folder"]+'/'+old_stream+'.csv:/content',headers={'Authorization': 'Bearer ' + result['access_token']} , data = content ).text )
                                     print ("risposta ricevuta %s " % response)
                                     # delete temporary file when upload is completed
                                     self._remove_temporary_file (self.base_file+old_stream+'.csv')
                                     break

             except StopIteration:
                  print ('nothing to do!')
                  #client.update_resource (resources[self.old_stream], body_json )
                  #break
                  #continue



    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        result = None

        try:
            # Verify whether OneDrive workspace is reachable
            #URL = 'https://login.microsoftonline.com/' + config['authority']
            app = msal.PublicClientApplication(config["client_id"], authority=config["authority"],  ) 
            if not result:
               result = app.acquire_token_by_username_password(config["username"], config["password"], scopes=["Files.ReadWrite"] )
            if "access_token" in result:
               return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else: 
               print(result.get("error"))
               print(result.get("error_description"))
               print(result.get("correlation_id"))  # You may need this when reporting a bug
               if 65001 in result.get("error_codes", []):  # Not mean to be coded programatically, but...
                     # AAD requires user consent for U/P flow
                     print("Visit this to consent:", app.get_authorization_request_url(scopes=["Files.ReadWrite"]))
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")

    def _create_temporary_file (self, abs_file_name:str, data: Mapping[str, Any] ):
        """
        create a CSV from JSON response 
        """
        with open (abs_file_name, 'w') as fp:
              write=csv.writer(fp, delimiter=',')
              write.writerow(data[0].keys())
              for k in data:
                write.writerow(k.values())

    def _remove_temporary_file (self, abs_file_name: str):
        os.remove (abs_file_name)

