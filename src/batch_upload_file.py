""" ładowanie pliku jsonl przez api OpenAI """
import os
import time
import glob
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
    if os.path.exists(analiza_path):
        os.remove(analiza_path)

    client = OpenAI()

    jsonl_dir = Path('..') / 'SGKP' / 'JSON' / f'batch_{DANE}'
    jsonl_files = glob.glob(str(jsonl_dir / f'sgkp_{VOLUME}_batch*.jsonl'))

    if jsonl_files:
        for out_f in jsonl_files:
            print(out_f)
            batch_input_file = client.files.create(
                file=open(out_f, "rb"),
                purpose="batch"
            )

            with open(analiza_path, 'a', encoding='utf-8') as f:
                f.write(batch_input_file.id + '\n')


    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
