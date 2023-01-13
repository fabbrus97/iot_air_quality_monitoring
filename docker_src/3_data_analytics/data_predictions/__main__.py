import data_predictions.predict
import datetime
import json
import time

def run():
    while True:
        try:
            settings = json.load(open("/workspace/settings.json"))

            predict_seconds = settings["predict_seconds"]
            sample_freq = settings["sample_frequency"]

            print("Configuration read")

            now = datetime.datetime.now()
            # prev_time = now - datetime.timedelta(seconds=predict_seconds*3) #use three times the amount of data we want to predict as training data
            prev_time = now - datetime.timedelta(days=1) # use 24 hours as training data

            prev_time = datetime.datetime.isoformat(prev_time) + "Z" #NOTE: if execute in docker container, the tz is UTC so in this case appending Z is correct
            now = datetime.datetime.isoformat(now) + "Z"

            print("Run predictions...")

            data_predictions.predict.predict("temperature", int(predict_seconds/sample_freq), sample_freq, prev_time, now)
            data_predictions.predict.predict("humidity", int(predict_seconds/sample_freq), sample_freq, prev_time, now)
            data_predictions.predict.predict("gas_concentration", int(predict_seconds/sample_freq), sample_freq, prev_time, now)

            print(f"Predictions done, next scheduled in {predict_seconds} seconds - ", datetime.datetime.isoformat(datetime.datetime.now() + datetime.timedelta(seconds=predict_seconds)))

            time.sleep(predict_seconds)
        except Exception as e:
            print(e)
            time.sleep(30)

if __name__ == "__main__":
    run()
    
