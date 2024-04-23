import requests
import re

# Prompt the user for the URL
url = input("Enter the URL: ")

try:
    # Fetch the HTML content of the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for non-2xx status codes
    html_content = response.text
except requests.exceptions.RequestException as e:
    print(f"Error fetching the URL: {e}")
    exit()

result_start = '<li class="arxiv-result">'
result_end = '</li>'

while True:
    start_index = html_content.find(result_start)
    if start_index == -1:
        break

    end_index = html_content.find(result_end, start_index) + len(result_end)
    result_html = html_content[start_index:end_index]

    pdf_start = 'https://arxiv.org/pdf/'
    pdf_link_start = result_html.find(pdf_start)
    if pdf_link_start != -1:
        pdf_link_end = result_html.find('"', pdf_link_start + len(pdf_start))
        pdf_link = result_html[pdf_link_start:pdf_link_end]
    else:
        print("No PDF link found")
        html_content = html_content[end_index:]
        continue

    title_start = '<p class="title is-5 mathjax">'
    title_end = '</p>'
    title_start_index = result_html.find(title_start)
    if title_start_index != -1:
        title_start_index += len(title_start)
        title_end_index = result_html.find(title_end, title_start_index)
        title = result_html[title_start_index:title_end_index]
    else:
        print("No title found")
        html_content = html_content[end_index:]
        continue

    # Remove special characters and leading/trailing tabs from the title
    filename = re.sub(r'[^a-zA-Z0-9 ]', '', title).strip('\t') + '.pdf'

    try:
        response = requests.get(pdf_link)
        with open(filename, 'wb') as pdf_file:
            pdf_file.write(response.content)
        print(f"Downloaded {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {pdf_link}: {e}")

    html_content = html_content[end_index:]
