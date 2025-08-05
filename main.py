import requests
import sys
import os
import json

CACHE_BREEDS = []

# Проверяем наличие породы
def get_dog_breed(breed_input: str):
    global CACHE_BREEDS

    words_breed = breed_input.strip().lower().split()

    if not words_breed:
        sys.exit('Вы не ввели название породы')

    url_all_breeds = 'https://dog.ceo/api/breeds/list/all'
    response_all_breeds = requests.get(url_all_breeds)
    CACHE_BREEDS = response_all_breeds.json()['message']

    main_breed = ''.join(words_breed)
    if main_breed in CACHE_BREEDS.keys():
        sub_breed = bool(CACHE_BREEDS[main_breed])
        return [main_breed], sub_breed

    breed_sub = [(words_breed[0], words_breed[1]), (words_breed[1], words_breed[0])]
    for breed, sub in breed_sub:
        if breed in CACHE_BREEDS.keys() and sub in CACHE_BREEDS[breed]:
            return [breed, sub], False
    sys.exit('Такой породы нет. Проверьте написание.')

# Получаем изображение собак
def get_dog_images(breed: list, sub: bool):
    list_files = []
    list_url_images = []
    if not sub:
        url_images = f'https://dog.ceo/api/breed/{'/'.join(breed)}/images'
        response_images = requests.get(url_images)
        data_images = response_images.json()
        list_url_images = data_images['message']
        list_files = [{'filename': f'{'_'.join(breed)}_{image_url.split('/')[-1]}'} for image_url in list_url_images]
    if sub:
        for sub in CACHE_BREEDS[breed[0]]:
            url_images = f'https://dog.ceo/api/breed/{breed[0]}/{sub}/images/random'
            response_images = requests.get(url_images)
            data_images = response_images.json()["message"]
            list_url_images.append(data_images)
            list_files.append({'filename': f'{breed[0]}_{sub}_{url_images.split('/')[-1]}'})
    with open("images.json", "w", encoding="utf-8") as f:
        json.dump(list_files, f, indent=1)
    return list_url_images

def put_images(urls: list):
    url_folder = 'https://cloud-api.yandex.net/v1/disk/resources'
    params_folder = {'path': f'{' '.join(check_breed)}'}
    headers = {'Authorization': f'OAuth {yd_token}'}
    requests.put(url_folder, headers=headers, params=params_folder)

    upload_image = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    for i, url in enumerate(urls):
        params_upload = {'path': f'disk:/{' '.join(check_breed)}/{' '.join(check_breed)} {url.split('/')[-1]}', 'url': url}
        requests.post(upload_image, headers=headers, params=params_upload)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'Загружено {(i+1)/len(urls)*100:.2f} %')
    return "Все изображения загружены"


if __name__ == "__main__":
    dog_breed_input = input('Введите породу на английском ')
    yd_token = input('Введите OAuth-токен Яндекс ')

    check_breed, check_sub_breed = get_dog_breed(dog_breed_input)
    urls_images = get_dog_images(check_breed, check_sub_breed)
    put_images(urls_images)