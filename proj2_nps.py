#################################
##### Name:
##### Uniqname:
#################################
#from requests_oauthlib import OAuth
from requests_oauthlib import OAuth1
from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
CACHE_FILENAME = "project2.json"
CACHE_DICT = {}

def open_cache():
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self,category,name,address,zipcode,phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    
    def info(self):
        return self.name + " (" + self.category + "): " + self.address + " " + self.zipcode
        


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    BASE_URL = "https://www.nps.gov"
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text,'html.parser')
    state_listing_parent = soup.find('ul',class_ = "dropdown-menu SearchBar-keywordSearch")
    state_dict = {}
    state_listing_divs = state_listing_parent.find_all('li',recursive = False)
    for state_listing_div in state_listing_divs:
        state_list_tag = state_listing_div.find('a')
        state_details_path = state_list_tag['href']
        state_id = state_listing_div.string.lower()
        state_dict[state_id] = BASE_URL + state_details_path
    return state_dict

def build_state_url_dict_with_cache():
    if "state_url_dict" in CACHE_DICT:
        print("Using cache")
        return CACHE_DICT["state_url_dict"]
    else:
        print("Fetching")
        CACHE_DICT["state_url_dict"] = build_state_url_dict()
        save_cache(CACHE_DICT)
        return CACHE_DICT["state_url_dict"]      

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    BASE_URL = site_url
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text,'html.parser')
    try:
        name = soup.find('div',class_ = "Hero-titleContainer clearfix").find('a').string.strip()
    except:
        name = "BLANK"
    try:
        category = soup.find('span',class_ = "Hero-designation").string.strip() 
    except:
        category = "BLANK"
    try:
        address = soup.find('span',itemprop = "addressLocality").string.strip() + ", "\
                + soup.find('span',itemprop = "addressRegion", class_ = "region").string.strip()
    except:
        address = "BLANK"
    try:
        zipcode = soup.find('span',itemprop = "postalCode", class_ = "postal-code").string.strip()
    except:
        zipcode = "BLANK"
    try:
        phone = soup.find('span',itemprop = "telephone", class_ = "tel").string.strip()
    except:
        phone = "BLANK"
    return NationalSite(category,name,address,zipcode,phone)

def get_site_instance_with_cache(site_url):
    if site_url in CACHE_DICT:
        print("Using cache")
        return NationalSite(CACHE_DICT[site_url]["category"],
                            CACHE_DICT[site_url]["name"],
                            CACHE_DICT[site_url]["address"],
                            CACHE_DICT[site_url]["zipcode"],
                            CACHE_DICT[site_url]["phone"])

    else:
        print("Fetching")
        temp = get_site_instance(site_url)
        CACHE_DICT[site_url] = temp.__dict__
        save_cache(CACHE_DICT)
        return NationalSite(CACHE_DICT[site_url]["category"],
                            CACHE_DICT[site_url]["name"],
                            CACHE_DICT[site_url]["address"],
                            CACHE_DICT[site_url]["zipcode"],
                            CACHE_DICT[site_url]["phone"])

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    BASE_URL = state_url
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text,'html.parser')
    site_object_list=[]
    park_list_parent = soup.find('ul', id = "list_parks")
    park_list_divs = park_list_parent.find_all('li', class_ = "clearfix",recursive = False)
    for park_list_div in park_list_divs:
        park_list_name = park_list_div.find('h3').find('a')['href']
        park_url = "http://www.nps.gov." + park_list_name
        park_object = get_site_instance_with_cache(park_url)
        site_object_list.append(park_object)
    return site_object_list

def get_sites_for_state_with_cache(state_url):
    if state_url in CACHE_DICT:
        print("Using cache")
        hold_list = []
        for val in CACHE_DICT[state_url]:
            print("Using cache")
            hold = NationalSite(val["category"],
                            val["name"],
                           val["address"],
                           val["zipcode"],
                           val["phone"])
            hold_list.append(hold)
        return hold_list
    else:
        print("Fetching")
        temp = get_sites_for_state(state_url)
        temp_list = []
        for t in temp:
            #temp_list = t.__dict__
            temp_list.append(t.__dict__)
        CACHE_DICT[state_url] = temp_list
        save_cache(CACHE_DICT)
        return temp    


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    BASE_URL = "https://www.mapquestapi.com/search/v2/radius"

    client_key = secrets.API_KEY
    client_secret = secrets.API_SECRECT

    oauth = OAuth1(client_key,
                client_secret=client_secret)

    params = {  "key":client_key,
                "origin":site_object.zipcode,
                "radius":10,
                "maxMatches":10,
                "ambiguities":"ignore",
                "outFormat":"json"}
    response = requests.get(BASE_URL,params = params,auth = oauth)

    results = response.json()

    return results
    

def get_nearby_places_with_cache(site_object): 
    if site_object.name in CACHE_DICT:
        print("Using cache")
        return CACHE_DICT[site_object.name]  
    else:
        print("Fetching")
        CACHE_DICT[site_object.name] = get_nearby_places(site_object)
        save_cache(CACHE_DICT)
        return CACHE_DICT[site_object.name] 


if __name__ == "__main__":
    CACHE_DICT = open_cache()
    state_name = input("Enter a state name(e.g. Michigan,michigan) or 'exit'\n")
    num = 0
    while state_name!="exit":
        #print("List of national sites in",state_name)
        state_dict = build_state_url_dict_with_cache()
        if state_name.lower() in state_dict:
            state_url = state_dict[state_name.lower()]
            object_list = get_sites_for_state_with_cache(state_url)
            print("List of national sites in",state_name)
            print("-----------------------------------")
            for instance in object_list:
                num = num+1
                print("[",num,"] ",instance.info())
            num = 0
            
            number_sel = input("Choose the number for further details or 'exit' or 'back' \n")
            while number_sel != "back":
                if number_sel =="exit":
                    break
                if (number_sel.isnumeric()) and (int(number_sel) <= len(object_list)):
                    site = object_list[int(number_sel)-1]
                    target_info = get_nearby_places_with_cache(site)
                    print("-----------------------------------") 
                    print("places near",site.name)
                    print("-----------------------------------") 
                    search_results = target_info["searchResults"]
                    for i in search_results:
                        name = i["name"]
                        if i["fields"]["group_sic_code_name"] == "":
                            category = "no category"
                            street_address = "no address, no city"
                        else:
                            category = i["fields"]["group_sic_code_name"]
                            street_address = i["fields"]["address"] + ", " + i["fields"]["city"] 
                        print("- " + name + " (" + category + "): " + street_address)
                else:
                    number_sel = print("[ERROR] Invalid Input \n")
                    number_sel = input("Choose the number for further details or 'exit' or 'back' \n")
                    if number_sel == "back":
                        break
                number_sel = input("Choose the number for further details or 'exit' or 'back' \n")
            if number_sel =="exit":
                break
            state_name = input("Enter a state name(e.g. Michigan,michigan) or 'exit'\n")
        else:
            state_name = print("[ERROR] Enter proper state name\n")
            state_name = input("Enter a state name(e.g. Michigan,michigan) or 'exit'\n")
    print("Bye")
    save_cache(CACHE_DICT)