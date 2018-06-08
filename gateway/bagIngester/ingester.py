import requests
import json
from django.http import HttpResponse

URL = "http://localhost:8000/aquariusMS/transformer/"


def retrieveBag(request):
    print("I have received a POST request!")
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    return json.dumps(json_data, indent=4, sort_keys=True)


def sendBag(request):
    # Takes in valid bag from POST
    contentbag = retrieveBag(request)
    # Send bag via POST to Aquarius
    response = requests.post(URL, data=contentbag)
    content = response.content
    print("Sending data to Aquarius...")
    return HttpResponse("The JSON was sent to " + content)
