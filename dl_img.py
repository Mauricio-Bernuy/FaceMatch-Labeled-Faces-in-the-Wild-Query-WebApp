
from bing_image_downloader import downloader

downloader.download('jason statham', limit=1,  output_dir='query', 
adult_filter_off=True, force_replace=False, timeout=60)