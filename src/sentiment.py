import requests
from time import sleep
import pandas as pd

from keys.keys import API_KEY, AUDIO_PATH, SENTIMENT_PATH

BUFFER = 5_242_880


def read_file(file):
    with open(file, "rb") as f:
        while True:
            audio = f.read(BUFFER)
            if not audio:
                break
            yield audio


def upload_audio(file):
    headers = {"authorization": API_KEY, "content-type": "application/json"}
    endpoint = "https://api.assemblyai.com/v2/upload"
    res_upload = requests.post(endpoint, headers=headers, data=read_file(file))
    upload_url = res_upload.json().get("upload_url")
    return upload_url


def submit_for_transcription(upload_url):
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = {"audio_url": upload_url, "sentiment_analysis": True, "speaker_labels": True}
    headers = {"authorization": API_KEY, "content-type": "application/json"}
    response = requests.post(endpoint, json=json, headers=headers)
    return response


def fetch_sentiment(response):
    current_status = "queued"
    response_id = response.json()["id"]
    endpoint = f"https://api.assemblyai.com/v2/transcript/{response_id}"
    headers = {"authorization": API_KEY}

    while current_status not in ("completed", "error"):
        response = requests.get(endpoint, headers=headers)
        current_status = response.json()["status"]
        if current_status in ("completed", "error"):
            print(response)
        else:
            sleep(10)

    return response


def parse_results(response):
    sent_data = []
    for idx, sentence in enumerate(response.json()["sentiment_analysis_results"]):
        sent = sentence["text"]
        sentiment = sentence["sentiment"]
        start = sentence["start"]
        stop = sentence["end"]
        duration = (sentence["end"] - sentence["start"]) / 1000
        speaker = sentence["speaker"]
        sent_data.append([idx + 1, sent, start, stop, duration, speaker, sentiment])
    cols = ["SentenceID", "Text", "Start", "Stop", "Duration", "Speaker", "Sentiment"]
    df = pd.DataFrame(sent_data, columns=cols)

    return df


if __name__ == "__main__":
    upload_url = upload_audio(AUDIO_PATH)
    response = submit_for_transcription(upload_url)
    response = fetch_sentiment(response)
    df = parse_results(response)
    df.to_csv(SENTIMENT_PATH, index=False)
