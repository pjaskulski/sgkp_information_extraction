""" gpt-4.1-mini - poprawne odczyty nazw pisanych boldem """
import os
import base64
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# pomiar czasu wykonania
start_time = time.time()

# API-KEY
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

MODEL = "gpt-4.1-mini"

client = OpenAI(api_key=OPENAI_API_KEY)


# ---------------------------- FUNCTIONS ---------------------------------------
def encode_image(image_path):
    """ image encode"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# @sleep_and_retry
# @limits(calls=30, period=60)
def generate(file_name:str):
    """ test obrazków z nazwami """

    base64_image = encode_image(file_name)

    base_file_name = os.path.basename(file_name)
    nazwa = base_file_name.replace('.png','')

    system_prompt = f"""
Act as a professional OCR system and proofreader.
Odczytaj dokładnie i wiernie tekst z załączonego obrazka, to nazwa hasła ze słownika geograficznego,
niekiedy z przecinkiem na końcu. Zwykły system ocr odczytał ten tekst jako "{nazwa}".
Zweryfikuj to i odczytaj poprawnie. Dokładność odczytu jest niezwykle ważna. Nie modyfikuj
wielkości liter (np. nie zmieniaj małych liter na duże na początku nazw, jeżeli tak jest
na obrazku).
Zweryfikuj liczbę znaków w obrazku i odczytaną liczbę znaków, powinny być zgodne.
Ważne: jeżeli tekst wygląda na kursywę (czcionkę pochyloną) pomiń odczytywanie, zwróć pusty tekst.
Zwróć tylko odczytany tekst.
"""

    response = client.responses.create(
        model=MODEL,
        input=[
            {
            "role": "user",
            "content": [
                {
                "type": "input_image",
                "image_url":  f"data:image/png;base64,{base64_image}",
                },
                {
                "type": "input_text",
                "text": system_prompt
                }
            ]
            }
        ],
        text={
            "format": {
                "type": "text"
            }
        },
        reasoning={},
        tools=[],
        temperature=0,
        max_output_tokens=2048,
        top_p=1,
        store=True
        )

    return response.output_text


# -------------------------------- MAIN ----------------------------------------
if __name__ == "__main__":
    directory = Path('..') / "tom_08_err"
    png_files = sorted([f for f in os.listdir(directory) if f.lower().endswith('.png')])

    path_out = Path('..') / "tom_08_err" / "sgkp_08_errors.html"
    if os.path.exists(path_out):
        os.remove(path_out)

    size = len(png_files)
    licznik = 0
    start = False

    if not os.path.exists(path_out):
        with open(path_out, 'a', encoding='utf-8') as f_out:
            f_out.write('<html><body><table border="1">\n')

    if png_files:
        for file in png_files:
            licznik += 1

            path_png = Path('..') / "tom_08_err" / file

            text = generate(path_png)

            include = False
            if text:
                old_text = file.replace(".png","").lower()
                new_text = text.lower()

                if old_text.endswith(','):
                    old_text = old_text[:-1]
                elif old_text.endswith('.'):
                    old_text = old_text[:-1]

                if new_text.endswith(','):
                    new_text = old_text[:-1]
                elif new_text.endswith('.'):
                    new_text = old_text[:-1]

                if old_text != new_text:
                    include = True

            if include:
                with open(path_out, 'a', encoding='utf-8') as f_out:
                    f_out.write(f'<tr><td>{file.replace(".png","")}</td><td><img src="{file}" alt="Fragment skanu" width="auto" height="auto"></td><td>{text}</td></tr>\n')

            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(f'{current_time} - {licznik}/{size}. {file}')


    with open(path_out, 'a', encoding='utf-8') as f_out:
        f_out.write('</table></body></html>\n')

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
