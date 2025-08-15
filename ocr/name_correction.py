""" korekta nazw haseł """
import os
import pymupdf  # PyMuPDF


def find_and_screenshot(pdf_path, search_term, output_dir=".", padding=20, dpi=300, last_page=0):
    """
    Wyszukuje pierwsze wystąpienie terminu w pliku PDF i zapisuje zrzut ekranu
    obszaru wokół niego jako plik PNG.
    """
    found = False
    output_filename = os.path.join(output_dir, f"{search_term}.png")

    os.makedirs(output_dir, exist_ok=True)

    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        print(f"Błąd: Nie można otworzyć pliku PDF '{pdf_path}'. {e}")
        return

    print(f"Przeszukiwanie pliku '{pdf_path}' w poszukiwaniu '{search_term}'...")

    try:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
           
            text_instances = page.search_for(search_term)

            if text_instances:
                for rect in text_instances:
                    text_in_box = page.get_textbox(rect)
                    print("text_in_box: " + text_in_box)
                    if search_term in text_in_box.strip():
                        print(f"Znaleziono '{search_term}' na stronie {page_num + 1} w obszarze: {rect}")

                        clip_rect = pymupdf.Rect(
                            max(0, rect.x0 - padding),
                            max(0, rect.y0 - padding),
                            min(page.rect.width, rect.x1 + padding),
                            min(page.rect.height, rect.y1 + padding)
                        )

                        pix = page.get_pixmap(clip=clip_rect, dpi=dpi)

                        pix.save(output_filename)
                        print(f"Zapisano zrzut ekranu do: '{output_filename}'")
                        found = True
                        break
            if found: break

        if not found:
            print(f"Nie znaleziono tekstu '{search_term}' w dokumencie.")

    except Exception as e:
        print(f"Wystąpił błąd podczas przetwarzania PDF: {e}")
    finally:
        doc.close()

    return page_num


if __name__ == "__main__":
    with open('../tom_07_wyprostowane/sgkp_07_weryfikacja.txt', 'r', encoding='utf-8') as f:
        lista = f.readlines()
        lista = [x.strip() for x in lista]

    pdf_file = '../tom_07_wyprostowane/sgkp_07_tesseract.pdf'
    output_dir = '../tom_07_err'

    p_num = 0
    for item in lista:
        if os.path.exists(f'../tom_07_err/{item}.png'):
            continue
        p_num = find_and_screenshot(pdf_file, item, output_dir, padding=2, last_page=p_num)
