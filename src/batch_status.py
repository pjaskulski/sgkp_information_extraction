""" status zadań przetwarzania przez API OpenAI """
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import openai
from openai import OpenAI


VOLUME = '01'
#DANE = 'dane_podstawowe'
DANE = 'wlasnosc_przemysl'
#DANE = 'instytucje_urzedy'
#DANE = 'statystyka'
#DANE = 'struktura'
#DANE = 'wlasnosc_ziemska'
ANALIZA = f'TOM_{VOLUME}_{DANE}.files'
BATCH_FILE = ANALIZA.replace('.files', '.batchs')
RESP_FILE = ANALIZA.replace('.files', '.responses')

# API-KEY
env_path = Path(".") / ".env_ihpan"
load_dotenv(dotenv_path=env_path)
OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
PROJECT_ID = os.environ.get('PROJECT_ID')
openai.api_key = OPENAI_API_KEY
openai.project = PROJECT_ID


# --------------------------------- MAIN ---------------------------------------
if __name__ == '__main__':

     # pomiar czasu wykonania
    start_time = time.time()

    # plik z identyfikatorami zadań
    batch_path = Path('..') / 'SGKP' / 'JSON' / BATCH_FILE
    with open(batch_path, 'r', encoding='utf-8') as f:
        batch_id_list = f.readlines()
        batch_id_list = [x.strip() for x in batch_id_list]

    # plik z identyfikatorami plików wynikowych - jeżeli zadanie zostało zakończone
    resp_path = Path('..') / 'SGKP' / 'JSON' / RESP_FILE
    if os.path.exists(resp_path):
        os.remove(resp_path)

    client = OpenAI()

    for batch_id in batch_id_list:
        print(batch_id)

        batch = client.batches.retrieve(batch_id)
        print(batch.status)
        if batch.status == 'completed':
            with open(resp_path, 'a', encoding='utf-8') as f:
                f.write(batch.output_file_id + '\n')

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
