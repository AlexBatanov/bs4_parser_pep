# Проект парсинга pep

Данный парсер предназначен для парсинга PEP документов и вывода результатов в заданном формате. 

## Установка и использование

1. Склонируйте репозиторий на свой компьютер:
    ```
   git clone git@github.com:AlexBatanov/bs4_parser_pep.git
    ```

2. Перейдите в папку проекта:
   ```
   cd bs4_parser_pep
   ```
   

3. Установите необходимые зависимости:
   ```
   pip install -r requirements.txt
   ```
   

4. Запуск парсера:
   ```
   cd src
   python3 main.py {positional argument} {optional argument}
   ```

   positional arguments:
   ```
   whats-new                    Cписок новых возможностей Python
   latest-versions              Cписок последних версий Python
   download                     Скачивает архив с документацией Python
   pep                          Статусы PEP документов и их количество
   ```


   optional arguments:
   ```
   -h, --help                   Show this help message and exit
   -c, --clear-cache            Очистка кеша
   -o, --output {pretty,file}   Дополнительные способы вывода данных
   ```
   
### Автор
[Batanov Alexandr](https://github.com/AlexBatanov)
