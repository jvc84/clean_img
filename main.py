## PBG > TIFF -> Contrast -> PDF

import cv2
from PIL import Image
import glob
import img2pdf
from pdf2image import convert_from_path
from io import BytesIO
from PIL import Image
import multiprocessing
import re

def sort_key(filename):
    match = re.search(r'(\d+)', filename) #Finds the first sequence of digits
    if match:
        return int(match.group(1)) #Returns the number as an integer
    else:
        return float('inf') #Non-numeric filenames will be put at the end



#### PNG to PDF
def convert_pngs_to_pdf(image_path_pattern, pdf_path):
    """Converts multiple PNG files to a single PDF.

    Args:
        image_path_pattern: A glob pattern (e.g., '*.png') to find PNG files.
        pdf_path: The path to save the resulting PDF file.
    """
    try:
        image_paths = glob.glob(image_path_pattern)
        if not image_paths:
            print(f"No PNG files found matching '{image_path_pattern}'.")
            return
        print(image_paths)

        sorted_paths = sorted(image_paths, key=sort_key)
        print(sorted_paths)


        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(sorted_paths))  # Pass the list of paths directly
        print(f"Successfully converted PNG files to '{pdf_path}'")
    except FileNotFoundError:
        print(f"Error: Could not find image files matching '{image_path_pattern}'. Check the path.")
    except Exception as e:
        print(f"An error occurred: {e}")


#### PDF to PNG
def pdf_to_png_memory( pdf_path, dpi=300):
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        png_images = []

        for image in images:
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = BytesIO(img_byte_arr.getvalue()) #resets byteIO cursor
            png_images.append(img_byte_arr)

        return png_images

    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


#### PNG to TIFF

def png_to_tiff_cv2(png_path, tiff_path):
    img = Image.open(png_path)
    img.save(tiff_path)

#### Contrast

def increase_contrast_fade_light(input_path, output_path, threshold=200):
    """Increases contrast and fades light colors to white, saving to a new file.

    Args:
        input_path: Path to the input image.
        output_path: Path to save the modified image.
        threshold: Threshold value (0-255). Pixels above this become white.
    """
    img = cv2.imread(input_path)
    if img is None:
        print(f"Error: Could not load image from {input_path}")
        return

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

    alpha = 1.5  # Contrast control (1.0-3.0)
    beta = 0     # Brightness control

    adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

    _, thresholded = cv2.threshold(adjusted, threshold, 255, cv2.THRESH_TOZERO)

    cv2.imwrite(output_path, thresholded)
    print(f"Image saved to {output_path}")


### TIFF to PDF

import glob
import img2pdf
import os

def  contrast_to_pdf(image_path, pdf_path):
    with open(pdf_path,"wb") as f:
        f.write(img2pdf.convert(glob.glob(image_path)))


#### Main
# png_to_tiff_cv2("source.png", "source.tiff")


def contrast_me(_i, _byte_array, _contrast_dir):
    print(_i, _byte_array, _contrast_dir)

    contrast_image_path_page = os.path.join(_contrast_dir, f"{_i+1}_page.png")
    img = Image.open(_byte_array)
    img.save(contrast_image_path_page)  # save to current directory.

    return 0




if __name__ == "__main__" :
    import time

    start_time = time.perf_counter()

    image_directory = "pics"
    cleared_image_directory = "cleared"
    contrasted_image_directory = "contrasted"
    image_path_pattern = os.path.join(image_directory, "*.png")
    convert_pngs_to_pdf(image_path_pattern,"source.pdf")

    os.makedirs(image_directory, exist_ok=True)
    os.makedirs(cleared_image_directory, exist_ok=True)
    os.makedirs(contrasted_image_directory, exist_ok=True)

    # pdf to png
    pdf_file = "source.pdf"
    png_byte_arrays = pdf_to_png_memory(pdf_file, dpi=200)


    if png_byte_arrays:
        list_exec = []
        # Process the PNG images in memory
        for i, byte_array in enumerate(png_byte_arrays):
            list_exec.append(
                (contrast_me, (i, byte_array, cleared_image_directory,),)
            )

        print(list_exec)

        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            results = []
            for f, args in list_exec:
                print(f, args)
                results.append(pool.apply_async(f, args))
            # results = [pool.apply_async(f, args) for f, args in [
            #     list_exec
            # ]]

            # print("Results: ", results)
            for r in results:
                print(r)
                r.wait()
            # _ = [r.get() for r in results]

    else :
        print("No byte arrays")
        exit(1)

    cleared_image_path_pattern = os.path.join(cleared_image_directory, "*.png")
    image_paths = glob.glob(cleared_image_path_pattern)

    tasks = [(img_path, os.path.join(contrasted_image_directory, os.path.basename(img_path))) for img_path in image_paths]

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.starmap(increase_contrast_fade_light, tasks) #Use starmap here to pass tuples


    contrasted_image_path_pattern = os.path.join(contrasted_image_directory, "*.png")
    convert_pngs_to_pdf(contrasted_image_path_pattern, "result.pdf")

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.6f}")