""" pobieranie wyników zadań przetwarzania przez Batch API OpenAI """
import os
import sys
import time
import glob
import json
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

    response_dir = Path('..') / 'SGKP' / 'JSON' / f'response_{DANE}'
    response_dir.mkdir(exist_ok=True)
    response_files = glob.glob(str(response_dir / '*.json'))

    if response_files:
        for resp_f in response_files:
            os.remove(resp_f)

    resp_path = Path('..') / 'SGKP' / 'JSON' / RESP_FILE
    with open(resp_path, 'r', encoding='utf-8') as f:
        resp_id_list = f.readlines()
        resp_id_list = [x.strip() for x in resp_id_list]

    client = OpenAI()

    for resp_id in resp_id_list:
        print(resp_id)

        resp_content = client.files.content(resp_id).read()
        results = [json.loads(line) for line in resp_content.splitlines()]

        for result in results:
            content_str = result["response"]["body"]["choices"][0]["message"]["content"]
            try:
                result["response"]["body"]["choices"][0]["message"]["content"] = json.loads(content_str)
            except Exception as e:
                print(f"BŁĄD odczytywania wyników: {e}", file=sys.stderr)
                result["response"]["body"]["choices"][0]["message"]["content"] = 'ERROR'

        resp_output_file = Path('..') / 'SGKP' / 'JSON' / f'response_{DANE}' / f'{resp_id}.json'

        with open(resp_output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
