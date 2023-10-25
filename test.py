from google_images_search import GoogleImagesSearch
gis = GoogleImagesSearch('AIzaSyC5uNFp0zfvsDeHg_6CA-F79ssycywQHX8', '35ed6304d1c67415a')
_search_params = {
    'q'       : '',
    'num'     : 1,
    'safe'    : 'high',
    'fileType': 'jpg|png',
    'imgType' : 'photo',
}
gis.search(search_params=_search_params)
for image in gis.results():
    print(image.url)