from .requests_wrapper import get, put, post, delete, print_response

from requests.auth import HTTPBasicAuth
import os

class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class BitbucketAuthen(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._username = os.environ["BITBUCKET_USERNAME"]
        self._app_password =  os.environ["BITBUCKET_PASSWORD"]
        self.base_api_1_0 = 'https://api.bitbucket.org/1.0'
        self.base_api_2_0 = 'https://api.bitbucket.org/2.0'
        self.base_internal = 'https://bitbucket.org/api/internal/workspaces'
        self.basic_auth=HTTPBasicAuth(self._username, self._app_password)

class Member:
    def __init__(self, uuid="", display_name="", email="") -> None:
        self.uuid = uuid
        self.display_name = display_name
        self.email = email
    
    def parser(self, raw_string):
        if "uuid" in raw_string:
            self.uuid = raw_string["uuid"]
        
        if "display_name" in raw_string:
            self.display_name = raw_string["display_name"]
        
        if "email" in raw_string:
            self.email = raw_string["email"]
        
    def __str__(self) -> str:
        return f"uuid = {self.uuid}\ndisplay_name = {self.display_name}\nemail = {self.email}\n"

#https://support.atlassian.com/bitbucket-cloud/docs/groups-endpoint/
class BitbucketGroup:
    def __init__(self, name, workspace) -> None:
        self.name = name
        self.workspace = workspace
        self.auth = BitbucketAuthen()
        self.members = {} #email:uuid
        self.base_api = self.auth.base_api_1_0
        # self.get_members()

    def get_members(self):
        self.members = {}

        def parser_members(response, returncode):
            next_page = ""
            if returncode == 200:
                next_page = ""  if not "next" in response else response["next"]

                users = response["values"]
                for i in users:
                    member = Member()
                    member.parser(i)
                    self.members[member.email] = member

                # index = "last" if next_page == "" else int(next_page.split("=")[-1]) - 1
                # with open(f"tmp/{self.workspace.name}/{self.name}_members_{index}.json", "w") as f:
                #     f.write(json.dumps(users, indent=2))
            return next_page

        URL = f'{self.auth.base_internal}/{self.workspace.name}/groups/{self.name}/members/'
        print(f"INFO: GET {URL}")
        response, returncode = get(URL, authen=self.auth.basic_auth)
        print_response(response, returncode)

        next_page = parser_members(response, returncode)

        while not next_page in ["", None]:
            URL = next_page
            print(f"INFO: GET {URL}")

            response, returncode = get(URL, authen=self.auth.basic_auth)
            print_response(response, returncode)
            next_page = parser_members(response, returncode)

    def create(self):
        URL = f'{self.base_api}/groups/{self.workspace.name}/'
        data = f"name={self.name}"
        print(f"INFO: POST {URL} data={data}")
        response, returncode = post(URL, authen=self.auth.basic_auth, data=data)
        print_response(response, returncode)

    def add_member(self, uuid):
        URL = f'{self.base_api}/groups/{self.workspace.name}/{self.name}/members/{uuid}/'
        print(f"INFO: PUT {URL}")
        response, returncode = put(URL, authen=self.auth.basic_auth, data='{}')
        print_response(response, returncode)

    #https://support.atlassian.com/bitbucket-cloud/docs/groups-endpoint/#DELETE-a-member
    def del_member(self, uuid):
        URL = f'{self.base_api}/groups/{self.workspace.name}/{self.name}/members/{uuid}/'
        print(f"INFO: DELETE {URL}")
        response, returncode = delete(URL, authen=self.auth.basic_auth)
        print_response(response, returncode)

#https://developer.atlassian.com/cloud/bitbucket/rest/intro/#authentication
class BitbucketWorkspace:
    def __init__(self, name) -> None:
        self.auth = BitbucketAuthen()
        self.name = name
        self.members = {} #uuid:display_name
        self.base_api = self.auth.base_api_2_0
        self.internal_api = self.auth.base_internal
        self.groups = {}
        # self.get_members()

    def get_members(self):
        self.members = {}

        def parser_members(response, returncode):
            next_page = ""
            if returncode == 200:
                next_page = ""  if not "next" in response else response["next"]

                users = response["values"]
                for i in users:
                    member = Member()
                    member.parser(i["user"])
                    self.members[member.uuid] = member

                # _index = "last" if next_page == "" else int(next_page.split("=")[-1]) - 1
                # os.makedirs(f"tmp/{self.name}", exist_ok=True)
                
                # with open(f"tmp/{self.name}/members_{_index}.json", "w") as f:
                #     f.write(json.dumps(users, indent=2))

            return next_page

        URL = f'{self.base_api}/workspaces/{self.name}/members/'
        print(f"INFO: GET {URL}")

        response, returncode = get(URL, authen=self.auth.basic_auth)
        print_response(response, returncode)
        next_page = parser_members(response, returncode)
 
        while not next_page in ["", None]:
            URL = next_page
            print(f"INFO: GET {URL}")

            response, returncode = get(URL, authen=self.auth.basic_auth)
            print_response(response, returncode)
            next_page = parser_members(response, returncode)

    def get_groups(self):
        self.groups = {}

        def parser_groups(response, returncode):
            if returncode == 200:
                next_page = ""  if not "next" in response else response["next"]

                groups = response["values"]
            
                for i in groups:
                    self.groups[i["slug"]] = BitbucketGroup(name=i["slug"], workspace=self)

                # _index = "last" if next_page == "" else int(next_page.split("=")[-1]) - 1
                # _path = f"tmp/{self.name}/groups_{_index}.json"
                # os.makedirs(f"tmp/{self.name}", exist_ok=True)

                # with open(_path, "w") as f:
                #     f.write(json.dumps(groups, indent=2))
                
                return next_page

        URL = f'{self.internal_api}/{self.name}/groups'
        print(f"INFO: GET {URL}")

        response, returncode = get(URL, authen=self.auth.basic_auth)
        print_response(response, returncode)
        next_page = parser_groups(response, returncode)
 
        while not next_page in ["", None]:
            URL = next_page
            print(f"INFO: GET {URL}")
            response, returncode = get(URL, authen=self.auth.basic_auth)
            print_response(response, returncode)
            next_page = parser_groups(response, returncode)