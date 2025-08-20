""" towrzenie zadań przetwarzania przez Batch API OpenAI """
import os
import time
from pathlib import Path
from dotenv import load_dotenv
import openai
from openai import OpenAI


VOLUME = '15'

DANE = 'dane_podstawowe'
#DANE = 'wlasnosc_przemysl'
#DANE = 'instytucje_urzedy'
#DANE = 'statystyka'
#DANE = 'struktura'
#DANE = 'wlasnosc_ziemska'
ANALIZA = f'TOM_{VOLUME}_{DANE}.files'
BATCH_FILE = ANALIZA.replace('.files', '.batchs')

# API-KEY
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY


# --------------------------------- MAIN ---------------------------------------
if __name__ == '__main__':

     # pomiar czasu wykonania
    start_time = time.time()

    analiza_path = Path('..') / 'SGKP' / 'JSON' / ANALIZA
    with open(analiza_path, 'r', encoding='utf-8') as f:
        file_id_list = f.readlines()
        file_id_list = [x.strip() for x in file_id_list]

    client = OpenAI()

    batch_path = Path('..') / 'SGKP' / 'JSON' / BATCH_FILE
    if os.path.exists(batch_path):
        os.remove(batch_path)

    for file_id in file_id_list:
        print(file_id)

        batch = client.batches.create(
            input_file_id=file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "description": f"analiza tomu {VOLUME} SGKP"
            }
        )

        with open(batch_path, 'a', encoding='utf-8') as f:
            f.write(batch.id + '\n')

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
