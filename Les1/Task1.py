import requests
import json

# Ввод пользователя:
username = 'LittleFox26'

response = requests.get(f"https://api.github.com/users/{username}/repos")
j_data = response.json()

# Вывод списка названий репозиториев пользователя:
for i in range(len(j_data)):
    print(j_data[i]['name'])

# Сохранение JSON-вывода в файле:
with open('user_repos.json', 'w') as f:
    f.write(response.text)
# Альтернативный вариант:
with open('user_repos1.json', 'w') as f:
    json.dump(j_data, f)
