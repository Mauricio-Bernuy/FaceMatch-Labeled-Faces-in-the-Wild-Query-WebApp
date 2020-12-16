
import requests
import modified_bing_downloader as downloader


while 1:
    name_input = input()
    name_input = "site:wikipedia.org " + name_input
    downloader.download(name_input, limit=1,  output_dir='test', 
    adult_filter_off=True, force_replace=False, timeout=30)
