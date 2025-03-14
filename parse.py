
import shutil
import os


def remove_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' removed successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except OSError as e:
        print(f"Error removing file '{file_path}': {e}")


def remove_dir(dir_path):
    try:
        os.rmdir(dir_path)
        print(f"Directory '{dir_path}' removed successfully.")
    except FileNotFoundError:
        print(f"Directory '{dir_path}' not found.")
    except OSError as e:
        print(f"Error removing directory '{dir_path}': {e}")


def mv_py(source_path, dest_path):
    try:
        shutil.move(source_path, dest_path)
        print(f"File/directory '{source_path}' moved to '{dest_path}' successfully.")
    except FileNotFoundError:
        print(f"Source '{source_path}' not found.")
    except OSError as e:
        print(f"Error moving '{source_path}': {e}")
    except shutil.Error as e:
        print(f"Error moving '{source_path}': {e}")


def check_empty_file(file_path):
    try:
        return os.stat(file_path).st_size == 0
    except FileNotFoundError:
        return False  # C


def check_empty_dir(dir_path):
    try:
        contents = os.listdir(dir_path)
        return len(contents) == 0
    except FileNotFoundError:
        return False
    except OSError:
        return False


def clean_backup_file(file_path):
    bak_path = f"{file_path}.bak"

    if not check_empty_file(file_path):
        remove_file(bak_path)
        mv_py(file_path, bak_path)


def clean_backup_dir(dir_path):
    bak_path = f"{dir_path}.bak"

    if not check_empty_dir(dir_path):
        remove_dir(bak_path)
        mv_py(dir_path, bak_path)


def remove_backups():
    dirs = ["pics", "contrasted", "cleared"]
    files = ["Viewer", "result.pdf"]

    for file in files:
        clean_backup_file(file)

    for dir in dirs:
        clean_backup_dir(dir)



def download_viewer():
    try:
        os.system("curl -b cookies.txt -O \"https://weblibranet.linguanet.ru/ProtectedView2022/App/Viewer\" || echo \"Didn't download  viewer\"")
    except Exception as e:
        print("Viewer was not downloaded")
def parse_viewer():
    all_pages = 0
    regid = 0
    token = ""

    with open("Viewer", 'r') as file:
        for line in file:
            if "Всего страниц в файле" in line:
                all_pages = int(line.split("/")[1].split("<")[0])
            elif "/ProtectedView2022/App/GetPage" in line:
                regid = int(line.split("{")[2].split("}")[0])
            elif "var token = " in line:
                token = line.split("\"")[1]

    print(f"All apges: {all_pages}, Regid: {regid}, Token: {token}")

    return  all_pages, regid, token


import multiprocessing

def download_page(page_number, regid, token):
    """Downloads a single page.  REPLACE THIS with your actual download code."""
    try:
        os.system(
            f"curl -b cookies.txt -o \"pics/page_{page_number}.png\" "
            f"\"https://weblibranet.linguanet.ru/ProtectedView2022/App/GetPage/{page_number}?token={token}&width=800&height=1131&resid={regid}\" "
        )
        print(f"Downloaded page {page_number}")
        return True  # Indicate successful download

    except Exception as e:
        print(f"Error downloading page {page_number}: {e}")
        return False  # Indicate download failure


def download_pages_in_batches(total_pages, regid, token, batch_size=10):
    """Downloads pages in batches using multiprocessing."""
    if total_pages <= 0:
        print("Number of pages must be positive.")
        return

    batches = []
    for i in range(0, total_pages, batch_size):
        start = i + 1
        end = min(i + batch_size + 1, total_pages + 1)
        batches.append(list(range(start, end)))

    #Use starmap instead of map
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        all_results = []
        for batch in batches:
            #Create a list of tuples; each tuple is a single argument for download_page
            batch_args = [(page, regid, token) for page in batch]
            batch_results = pool.starmap(download_page, batch_args)
            all_results.extend(batch_results)

    # Check for errors
    if False in all_results:
        print("Errors occurred during download.")
    else:
        print("All pages downloaded successfully.")


def prepare_and_download():
    os.makedirs("pics", exist_ok=True)
    os.makedirs("cleared", exist_ok=True)
    os.makedirs("contrasted", exist_ok=True)

    remove_backups()
    download_viewer()

    all_pages, regid, token =  parse_viewer()

    with open("urls.txt", 'w') as file:
        file.write('')

    if all_pages != 0 and regid != 0:
        download_pages_in_batches(all_pages, regid, token, batch_size=20)

    else:
        print("Zero value detected:")
        print(f"\tAll pages: {all_pages}")
        print(f"\tRegid: {regid}")


    
