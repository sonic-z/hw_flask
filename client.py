import requests

print('Добавление пользователя')
response = requests.post("http://127.0.0.1:5000/user",
                        json={"name": 'user1', 'password': 'gsgertyg323523'},
                       )
print(response.status_code)
print(response.json())
#
print('Добавление объявления')
response = requests.post("http://127.0.0.1:5000/ads",
                         json={"header": 'Заголовок объявления 1',
                               'text': 'text 1111111',
                               'price': '1000', 'owner_id': '1'},
                         )
print(response.status_code)
print(response.json())

# response = requests.patch("http://127.0.0.1:5000/ads/1/",
#                         json={"price": '1111'},
#                         )
# print(response.status_code)
# print(response.json())

# response = requests.delete(
#    "http://127.0.0.1:5000/ads/1/",
# )
# print(response.status_code)
# print(response.json())

print('Получение объявления')
# response = requests.get(
#    "http://127.0.0.1:5000/ads/1",
# )
# print(response.status_code)
# print(response.json())
