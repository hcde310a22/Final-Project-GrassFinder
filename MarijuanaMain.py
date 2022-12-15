import csv
from flask import Flask, render_template, request
import json
import requests
import random

fname = "cannabis.csv"

def get_emotion(sentence = ""):
    url = "https://api.apilayer.com/text_to_emotion"
    payload = sentence.encode("utf-8")
    headers = {
        "apikey": "PVWq14zMbVbmwon3DsDjFWDxQRAs3i5a"
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    status_code = response.status_code
    result = response.text
    print(result)
    result2 = json.loads(result)

    return result2

def sortKeysByValueEmotion(dict):
  keys = dict.keys()
  return sorted(keys, key=lambda k: dict[k], reverse=True)

def get_effects(feelingdict):
    if feelingdict == "Happy":
        new_list = ["Energetic", "Euphoric", "Talkative", "Creative", "Giggly"]
    elif feelingdict == "Angry":
        new_list = ["Relaxed", "Sleepy", "Happy", "Uplifted", "Hungry"]
    elif feelingdict == "Surprise":
        new_list = ["Creative", "Focused", "Talkative", "Tingly", "Aroused"]
    elif feelingdict == "Sad":
        new_list = ["Energetic", "Euphoric", "Uplifted", "Happy", "Giggly"]
    else:
        new_list = ["Relaxed", "Uplifted", "Sleepy", "Aroused", "Euphoric"]
    return new_list

def read_in(fname):
    straindict = {}
    with open(fname, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            # row = row.split(",")
            strainname = row[0]
            type = row[1]
            effects = row[3].split(',')
            caption = row[5]

            singlestrain = {
                "Type": type,
                "Effects": effects,
                "Caption": caption
            }

            straindict[strainname] = singlestrain

    # print(straindict)
    return straindict

def get_strains(desired_effects_list, straindict):
    #go through each strain
    for strain in straindict:
        score = 0
        #goes throguh each effect in the list we made aka 3 times
        for effect in desired_effects_list:
            if effect in straindict[strain]['Effects']:
                score+=1
        straindict[strain]['Score'] = score
    return straindict

def filterstrains(typedict):
    new_dict = {}
    for strain in typedict:
        if typedict[strain]['Score'] >= 4:
            new_dict[strain] = typedict[strain]
    choice = random.choice(list(new_dict.keys()))
    return choice

app = Flask(__name__)
@app.route("/")
def main_handler():
    app.logger.info("In MainHandler")
    personname = request.args.get('name')
    if personname:
        feelingsentence = request.args.get('feeling')

        if feelingsentence is not None:
            dict1 = get_emotion(feelingsentence)
            feelingdict = sortKeysByValueEmotion(dict1)
            actualfeeling = feelingdict[0]
            straindict = read_in(fname)
            effectlist = get_effects(actualfeeling)
            straindict = get_strains(effectlist, straindict)

            sativadict = {}
            indicadict = {}
            hybriddict = {}

            for strain in straindict:
                if straindict[strain]['Type'] == "sativa":
                    sativadict[strain] = straindict[strain]
                elif straindict[strain]['Type'] == "indica":
                    indicadict[strain] = straindict[strain]
                elif straindict[strain]['Type'] == "hybrid":
                    hybriddict[strain] = straindict[strain]

            sativastrainchoice = filterstrains(sativadict)
            indicastrainchoice = filterstrains(indicadict)
            hybridstrainchoice = filterstrains(hybriddict)
            sativastrainscore = str(sativadict[sativastrainchoice]['Score'])
            indicastrainscore = str(indicadict[indicastrainchoice]['Score'])
            hybridstrainscore = str(hybriddict[hybridstrainchoice]['Score'])
            sativastraincaption = str(sativadict[sativastrainchoice]['Caption'])
            indicastraincaption = str(indicadict[indicastrainchoice]['Caption'])
            hybridstraincaption = str(hybriddict[hybridstrainchoice]['Caption'])

            title = "Thanks for responding %s"%personname
            return render_template('WeedTest.html',
                    page_title=title,
                    personname=personname,
                    feelingsentence = feelingsentence,
                    actualfeeling = actualfeeling,
                    sativastrainchoice = sativastrainchoice,
                    indicastrainchoice = indicastrainchoice,
                    hybridstrainchoice = hybridstrainchoice,
                    sativastrainscore = sativastrainscore,
                    indicastrainscore = indicastrainscore,
                    hybridstrainscore = hybridstrainscore,
                    sativastraincaption = sativastraincaption,
                    indicastraincaption = indicastraincaption,
                    hybridstraincaption = hybridstraincaption,
                    )

        else:
            return render_template('WeedTest.html',
                        page_title="Emotion Test - Error",
                        prompt="Something went wrong with the API Call")
    elif personname=="":
        return render_template('WeedTest.html',
                page_title="Form - Error",
                prompt="We need your name :/")
    else:
        return render_template('WeedTest.html',page_title="Something's gone wrong mate")

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
