#!/usr/bin/env python3
import os
import argparse
from PIL import Image, ImageDraw, ImageStat

def detect_header_end_y(image,
                        max_scan_percent=15.0,
                        min_whitespace_height_px=50,
                        pixel_white_threshold=75,
                        row_whiteness_threshold=0.97,
                        min_header_content_height_px=50,
                        min_main_content_after_whitespace_px=10 
                       ):
    """
    Próbuje wykryć koniec nagłówka
    """
    if image.mode != 'L':
        img_gray = image.convert('L')
    else:
        img_gray = image

    width, height = img_gray.size
    pixels = img_gray.load()

    max_scan_y = int(height * (max_scan_percent / 100.0))

    # Wymagania minimalne
    if max_scan_y < (min_header_content_height_px + min_whitespace_height_px + min_main_content_after_whitespace_px):
        print("  Debug: Obszar skanowania zbyt mały dla minimalnych wymagań wzorca.")
        return 0

    y = 0
    
    first_non_white_row_y_of_header = -1
    while y < max_scan_y:
        is_current_row_white = True
        non_white_count = 0
        for x_coord in range(width):
            if pixels[x_coord, y] <= pixel_white_threshold:
                non_white_count += 1

        if (non_white_count / width) > (1.0 - row_whiteness_threshold):
            is_current_row_white = False

        if not is_current_row_white:
            first_non_white_row_y_of_header = y
            break
        y += 1

    if first_non_white_row_y_of_header == -1:
        print("  Debug: Nie znaleziono żadnej treści (nie-białych wierszy) w obszarze skanowania.")
        return 0 

    last_non_white_row_y_of_header = -1
    consecutive_white_rows_count = 0

    y = first_non_white_row_y_of_header
    while y < max_scan_y:
        is_current_row_white = True
        non_white_count = 0
        for x_coord in range(width):
            if pixels[x_coord, y] <= pixel_white_threshold:
                non_white_count += 1

        if (non_white_count / width) > (1.0 - row_whiteness_threshold):
            is_current_row_white = False

        if not is_current_row_white: 
            last_non_white_row_y_of_header = y 
            consecutive_white_rows_count = 0 
        else:
            consecutive_white_rows_count += 1

            if consecutive_white_rows_count >= min_whitespace_height_px and last_non_white_row_y_of_header != -1:
                
                current_header_content_height = (last_non_white_row_y_of_header - first_non_white_row_y_of_header + 1)

                if current_header_content_height >= min_header_content_height_px:
                
                    whitespace_block_start_y = last_non_white_row_y_of_header + 1
                
                    current_whitespace_block_end_y = last_non_white_row_y_of_header + consecutive_white_rows_count

                    start_scan_main_content_y = current_whitespace_block_end_y + 1
                    main_content_found_height = 0

                    for y_main in range(start_scan_main_content_y,
                                        min(max_scan_y, start_scan_main_content_y + min_main_content_after_whitespace_px + 350)): # +350 by złapać poczatek tekstu
                        if y_main >= height: break 

                        is_main_content_row_white = True
                        mc_non_white_count = 0
                        for x_main in range(width):
                            if pixels[x_main, y_main] <= pixel_white_threshold:
                                mc_non_white_count +=1

                        if (mc_non_white_count / width) > (1.0 - row_whiteness_threshold): # Wiersz NIE jest biały
                            is_main_content_row_white = False

                        if not is_main_content_row_white:
                            main_content_found_height +=1
                            if main_content_found_height >= min_main_content_after_whitespace_px:
                                
                                print(f"  Debug: Wzorzec znaleziony. Nagłówek: {first_non_white_row_y_of_header}-{last_non_white_row_y_of_header} (wys: {current_header_content_height}px). "
                                      f"Biała przestrzeń: {whitespace_block_start_y}-{current_whitespace_block_end_y} (wys: {consecutive_white_rows_count}px). "
                                      f"Treść główna od y={start_scan_main_content_y} (znaleziono wys: {main_content_found_height}px). "
                                      f"Usuwam do y={whitespace_block_start_y}.")
                                return whitespace_block_start_y

                    print(f"  Debug: Nagłówek ({current_header_content_height}px) i biała przestrzeń ({consecutive_white_rows_count}px) OK, ale za mało treści po (tylko {main_content_found_height}px).")
                    consecutive_white_rows_count = 0

        y += 1 

    print("  Debug: Nie znaleziono pełnego wzorca 'nagłówek -> biała przestrzeń -> treść główna'.")
    return 0 


def process_image(image_path, output_path, fill_color="white", detection_params=None):
    if detection_params is None:
        detection_params = {}

    try:
        img_orig = Image.open(image_path)
        img_to_process = img_orig.copy()
        draw = ImageDraw.Draw(img_orig)
        width, height = img_orig.size

        height_to_remove = detect_header_end_y(img_to_process, **detection_params)

        if height_to_remove > 0:
            rectangle_coords = (0, 0, width, height_to_remove)
            draw.rectangle(rectangle_coords, fill=fill_color)
            img_orig.save(output_path)
            print(f"Przetworzono: {image_path} -> {output_path} (automatycznie zamalowano {height_to_remove}px nagłówka)")
        else:
            img_orig.save(output_path)
            print(f"Nie wykryto nagłówka do usunięcia w: {image_path}. Plik skopiowany/zapisany bez zmian do {output_path}")

    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {image_path}")
    except Exception as e:
        print(f"Błąd podczas przetwarzania {image_path}: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description="Automatycznie wykrywa i zamalowuje nagłówki na obrazach, jeśli pasują do wzorca.")
    parser.add_argument("input_dir", help="Folder z oryginalnymi obrazami.")
    parser.add_argument("output_dir", help="Folder, gdzie zostaną zapisane przetworzone obrazy.")
    parser.add_argument("--fill-color", type=str, default="white",
                        help="Kolor do zamalowania nagłówka (domyślnie: white).")

    # Parametry detekcji
    parser.add_argument("--max-scan-percent", type=float, default=15.0,
                        help="Maksymalny procent wysokości obrazu do skanowania (dom: 25.0).")
    parser.add_argument("--min-whitespace-px", type=int, default=50,
                        help="Minimalna wysokość (w px) ciągłej białej przestrzeni PO treści nagłówka (dom: 15).")
    parser.add_argument("--pixel-white-thr", type=int, default=125, choices=range(0,256), metavar="[0-255]",
                        help="Próg jasności piksela, aby uznać go za biały (dom: 235).")
    parser.add_argument("--row-white-thr", type=float, default=0.97, choices=[i/100 for i in range(0,101)], metavar="[0.0-1.0]",
                        help="Minimalny procent białych pikseli w wierszu, aby uznać go za 'biały wiersz' (dom: 0.97).")
    parser.add_argument("--min-header-content-px", type=int, default=50,
                        help="Minimalna wysokość (w px) samej treści nagłówka PRZED białą przestrzenią (dom: 10).")
    parser.add_argument("--min-main-content-px", type=int, default=10,
                        help="Minimalna wysokość (w px) treści głównej, która musi wystąpić PO białej przestrzeni za nagłówkiem (dom: 10).")

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Błąd: Folder wejściowy '{args.input_dir}' nie istnieje.")
        return

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"Utworzono folder wyjściowy: {args.output_dir}")

    detection_params = {
        "max_scan_percent": args.max_scan_percent,
        "min_whitespace_height_px": args.min_whitespace_px,
        "pixel_white_threshold": args.pixel_white_thr,
        "row_whiteness_threshold": args.row_white_thr,
        "min_header_content_height_px": args.min_header_content_px, # Zmieniona nazwa parametru
        "min_main_content_after_whitespace_px": args.min_main_content_px
    }

    supported_extensions = ('.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif')

    for filename in sorted(os.listdir(args.input_dir)):
        if filename.lower().endswith(supported_extensions):

            input_path = os.path.join(args.input_dir, filename)
            output_filename = filename
            output_path = os.path.join(args.output_dir, output_filename)

            process_image(input_path, output_path,
                          fill_color=args.fill_color,
                          detection_params=detection_params)
        else:
            print(f"Pomijanie pliku o nieobsługiwanym rozszerzeniu: {filename}")

    print("Zakończono przetwarzanie.")

if __name__ == "__main__":
    main()
