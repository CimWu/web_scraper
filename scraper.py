import argparse
import urllib.request
import re
import os
from urllib.parse import urlparse
import urllib.error
from datetime import datetime

seen = list()


def search_links(url, depth, the_folder_name):
    # Cast depth to an integer
    depth = int(depth)

    # Connect to a URL and check if it has been seen before
    if url.startswith("http://") or url.startswith("https://") and url not in seen:

        try:
            # Open the URL and extract the HTML content
            with urllib.request.urlopen(url) as response:
                html_content = response.read().decode('iso-8859-1')

        except urllib.error.HTTPError as e:
            http_error = f"Error: {e}"
            print(http_error)

            with open(os.path.join(the_folder_name, "__error_log.txt"), "a", encoding="utf-8") as httperr_file:
                write_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                httperr_file.write(f"[{write_time}] {http_error}\n")
            return

        except Exception as e:
            err_msg = f"Error: {e}"
            print(err_msg)

            with open(os.path.join(the_folder_name, "__error_log.txt"), "a", encoding="utf-8") as err_file:
                write_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                err_file.write(f"[{write_time}] {err_msg}\n")
            return

        # Extract all the links from the HTML content
        links = re.findall('href="(.*?)"', html_content)

        # Add the current URL to the seen list
        seen.append(url)

        # Extract the filename from the URL and remove any query strings
        filename = url.split("/")[-1].split("?")[0]

        # If the filename is empty, set it to index.html
        if not filename:
            filename = "index.html"

        # Set the full path to the output file
        filepath = os.path.join(the_folder_name, re.sub(r'[^\w_.)( -]', '', filename))

        # Write the HTML content to a file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Recursively search the links but keep track of depth
        if depth > 1:
            for link in links:
                abs_link = urllib.parse.urljoin(url, link)
                search_links(abs_link, depth - 1, the_folder_name)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Webpage link scraper")
    parser.add_argument("--url", action="store", dest="url", required=True)
    parser.add_argument("--depth", action="store", dest="depth", default=2)
    given_args = parser.parse_args()

    # Create folder based on domain name
    domain_name = urlparse(given_args.url).netloc
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{domain_name.replace('.', '_')}_{timestamp}_{given_args.depth}"
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    try:
        search_links(given_args.url, given_args.depth, folder_name)
    except KeyboardInterrupt:
        print("Aborting the search")
        error_message = "Search aborted by user"
        with open(os.path.join(folder_name, "__error_log.txt"), "a", encoding="utf-8") as error_file:
            check_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_file.write(f"[{check_stamp}] {error_message}\n")
