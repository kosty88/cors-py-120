import requests
import datetime
import json
import configparser
from tqdm import tqdm

congig = configparser.ConfigParser()
congig.read('settings.ini')
vk_tk = congig['TOKENS']['vk_token']
yd_tk = congig['TOKENS']['yd_token']


class VK:
    all_list = []
    json_list = []

    def __init__(self, token_vk, version='5.199'):
        self.params = {
            'access_token': token_vk,
            'v': version
        }
        self.base = 'https://api.vk.com/method/'
        #self.all_list = []
        #self.json_list = []

    def get_photos(self, user_id, alb_id, maxcount=5):
        url = f'{self.base}photos.get'
        params = {
            'owner_id': user_id,
            'count': maxcount,
            'album_id': alb_id,
            'extended': 1
        }
        params.update(self.params)
        response = requests.get(url, params=params)
        kill = response.json()['response']['items']
        for i in kill:
            likes_num = i['likes']['count']             # взяли количество лайков у фотографии
            if likes_num in self.all_list:
                self.all_list.append(f'{likes_num}_{datetime.date.today()}')   # если кол-во лайков есть в списка добавляем дату
            else:
                self.all_list.append(likes_num)
            list_size = []
            for t in i['sizes']:
                list_size.append(t['type'])
            max_list = max(list_size)                    # буква МАХ фотографии
            self.all_list.append(max_list)
            if t['type'] == max_list:
                list_url = (t['url'])                   # URL МАХ фотографии
                self.all_list.append(list_url)
        # return self.json_list


class YD(VK):

    def __init__(self, token_yd, folder_name):
        self.token_yd = token_yd
        self.folder_name = folder_name

    def create_folder(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            'path': self.folder_name
            }
        headers = {
            'Authorization': self.token_yd
        }
        response = requests.put(url, params=params, headers=headers)

    def upload_file(self):
        i = 2
        for nam in tqdm(self.all_list[::3]):
            json_dict = {}
            name_url = self.all_list[i]
            filename = f'{nam}'+'.jpg'
            json_dict = {"file_name": filename,
                         "size": self.all_list[i-1]}
            self.json_list.append(json_dict)
            headers = {'Authorization': self.token_yd}
            params = {'path': f'/{self.folder_name}/' + filename, 'url': name_url}
            response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload', headers=headers,
                                     params=params)
            i += 3

    def create_json(self):
        with open('result.json', 'w', encoding='utf-8') as f:
            json.dump(self.json_list, f, ensure_ascii=False, indent=0, separators=(',', ': '))


if __name__ == "__main__":
    for i in range(3):
        use_id = input("Введите id пользователя: ")
        if use_id.isdecimal():
            vk_connector = VK(vk_tk)
            yd_connector = YD(yd_tk, use_id)
            for k in range(3):
                alb_id = input("Введите название папки откуда будут скачаны фото: 1 - PROFILE, 2 - WALL : ")
                if alb_id == "1":
                    vk_connector.get_photos(use_id, 'profile')
                    break
                elif alb_id == "2":
                    vk_connector.get_photos(use_id, 'wall')
                    break
                else:
                    if i == 1:
                        print(f'Ошибка! Вы ввели неверное число. Осталось {2 - k} попытка')
                    else:
                        print(f'Ошибка! Вы ввели неверное число. Осталось {2 - k} попыток')
            yd_connector.create_folder()
            yd_connector.upload_file()
            yd_connector.create_json()
            break
        else:
            if i == 1:
                print(f'Ошибка! id должен состоять только из цифр. Осталось {2 - i} попытка')
            else:
                print(f'Ошибка! id должен состоять только из цифр. Осталось {2-i} попыток')