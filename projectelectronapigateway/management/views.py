import json
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .forms import apiURLForm
from django.shortcuts import render, redirect

# # #
# class Bunch:
#     def __init__(self, url1, url2, url3):
#         self.url1 = url1
#         self.url2 = url2
#         self.url3 = url3


@csrf_exempt
def index(request):
    return HttpResponse(get_URL(request))


@csrf_exempt
def get_URL(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = apiURLForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()

            # # # process the data in form.cleaned_data as required/place in a urlbunch
            # url1 = form.cleaned_data['URL_1']
            # url2 = form.cleaned_data['URL_2']
            # url3 = form.cleaned_data['URL_3']
            # urlbunch = Bunch(url1, url2, url3)

            # # # create payload and send
            # payload = {'key1': urlbunch.url1, 'key2': urlbunch.url2, 'key3': urlbunch.url3}
            # r = requests.post('http://localhost:8000/management/results', params=payload)
            # r = requests.get('http://localhost:8000/management/results', params=payload)
            # urlbunch.save()

            # # # redirect to a new URL:
            # return redirect(results)

            print(checkForBag(form['url1'].value()))

            url = apiURL.objects

            return render(request, 'management/results.html', {'form': form})

    # if a GET (or any other method) call apiURLForm 
    else:
        form = apiURLForm()
    return render(request, 'management/name.html', {'form': form})


def checkForBag(url):
    r = requests.get(url)
    return r.text


def receiveBag(request):
    print("I have received a POST request!")
    json_data = json.loads(request.body.decode(encoding='UTF-8'))
    return json.dumps(json_data, indent=4, sort_keys=True)


def sendBag(request):
    # Takes in valid bag from POST
    contentbag = receiveBag(request)
    # Send bag via POST to Aquarius
    response = requests.post(URL, data=contentbag)
    content = response.content
    print("Sending data to Aquarius...")
    return HttpResponse("The JSON was sent to " + content)


# # #
# @csrf_exempt
# def results(request):
#     print("This is the results func")
#     contentbag = showURL(request)
#     print(contentbag)
#     return HttpResponse("This is the results func")

# # #
# def showURL(request):
#     if request.method == 'POST':
#         print("I have received a POST request!")
#         res = request.POST.get('key1')
#         # print(res + "              WOW")
#         # return json.dumps(json_data, indent=4, sort_keys=True)
#         return HttpResponse("This is a wow")

