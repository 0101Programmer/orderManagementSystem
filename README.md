# «Order Management System» — полнофункциональное веб-приложение на Django для управления заказами в кафе. Приложение позволяет добавлять, удалять, искать, изменять и отображать заказы.

# Стек технологий:
+ Python 3.8+
+ Django 4+
+ HTML/CSS
+ PostgreSQL

# Функциональные требования:
+ Добавление заказа
+ Удаление заказа
+ Поиск заказа
+ Отображение всех заказов
+ Изменение статуса заказа
+ Расчет выручки за смену

# Дополнительные требования:
+ Хранение данных (PostgreSQL)
+ Обработка ошибок
+ CRUD операции
+ REST API
+ ООП

# Инструкция по развертыванию проекта:
## #1 Создание файла .env на одном уровне с файлом settings.py в папке "order_management_system"
![Снимок экрана 2025-03-07 205947](https://github.com/user-attachments/assets/f7e41dab-bccd-4b4a-8c0d-0382193260b6)

## Со следующими переменными (значения берутся свои): 

![capture_250307_210037](https://github.com/user-attachments/assets/1fac9d8f-73d1-44f1-9957-49c09101d700)

## #2 Создание виртуального окружения (если оно не создано и не активировано)

> python -m venv .venv

## Его активация

> .venv\Scripts\activate

## Установка зависимостей
> pip install -r requirements.txt

## #3 Запуск сервера

> cd order_management_system

> python manage.py runserver


![Снимок экрана 2025-03-07 210526](https://github.com/user-attachments/assets/091650e7-9b6f-499e-a4f0-d952cdebed06)

# Обзор функционала приложения через веб-интерфейс.

## # Главная страница

![Снимок экрана 2025-03-08 064129](https://github.com/user-attachments/assets/ee6abc09-f002-4894-ba7a-c391d56a375f)


Со стартовой страницы можно попасть на следующие:

+ Добавление (заказа)
+ Удаление
+ Поиск
+ Получение всех заказов
+ Изменение статуса заказа
+ Расчёт выручки за смену

## # Добавление заказа

### Тут можно добавить заказ в базу данных, присутствует валидация, что позволяет контролировать, что все заказы будут в едином стиле.

![Снимок экрана 2025-03-08 064446](https://github.com/user-attachments/assets/41a23d26-bf2d-415d-af5b-e306e8a14e60)


### Добавим пару заказов с корректными данными, увидим их в БД

![capture_250308_064626](https://github.com/user-attachments/assets/e5eb0e52-240a-4de8-819b-965229b1e444)

![Снимок экрана 2025-03-08 064743](https://github.com/user-attachments/assets/9a66690a-7079-454a-a018-a3e88a376341)

### Поля с ID, итоговой ценой заказа и статусом заполняются автоматически

![Снимок экрана 2025-03-08 064811](https://github.com/user-attachments/assets/193e77ae-5e05-4b82-860d-3b134619afe0)

### Попробуем отправить данные не по шаблону

![Снимок экрана 2025-03-08 065304](https://github.com/user-attachments/assets/a5043599-b6b5-4bc7-b6a0-dc679ecee599)

### Получаем ошибку 

![Снимок экрана 2025-03-08 065314](https://github.com/user-attachments/assets/c450af0e-bdad-4044-983f-e20a3ae17c9a)


## # Удаление заказа

### Как ясно из названия, тут можно удалить заказ из базы данных. Для этого реализован выпадающий список, из которого можно выбрать заказ по его ID и, соответственно, удалить


![Снимок экрана 2025-03-08 065624](https://github.com/user-attachments/assets/60489924-de5b-4d89-a700-f586ad041d72)

### Удалим заказ с ID 2


![Снимок экрана 2025-03-08 065632](https://github.com/user-attachments/assets/6fc031f1-c744-4a32-b000-3c17c163beda)


### В БД его также больше не увидим


![Снимок экрана 2025-03-08 065643](https://github.com/user-attachments/assets/bada2e3b-e3f0-4191-805c-ab927566f6b6)

## # Поиск заказа

### Заказы можно искать либо по номеру стола, либо по статусу заказа

![Снимок экрана 2025-03-08 070019](https://github.com/user-attachments/assets/8866a455-336e-4992-bb76-a8edb33175d7)

### Для демонстрации создадим ещё несколько заказов и попробуем их отобразить

![Снимок экрана 2025-03-08 070253](https://github.com/user-attachments/assets/39077dee-c75f-4ac2-b79c-66162c4e6f8b)


![Снимок экрана 2025-03-08 070303](https://github.com/user-attachments/assets/cbec7bb1-f550-490b-b052-9790db6c18ac)


![Снимок экрана 2025-03-08 070320](https://github.com/user-attachments/assets/7b0db1b9-8cfd-43d7-a810-20cd5cd8116f)


![Снимок экрана 2025-03-08 070329](https://github.com/user-attachments/assets/f16ff4d5-8324-4dd3-98ff-2b7cc8bfb6a5)

### Если попытаься найти заказы по двум условиям, то отобразится ошибка


![Снимок экрана 2025-03-08 070457](https://github.com/user-attachments/assets/93ad6c5e-07ce-4536-b5a7-227fd487cdbd)

### Поиск заказа по несуществующему номеру стола не отобразит никаких данных

![Снимок экрана 2025-03-08 070631](https://github.com/user-attachments/assets/1c83bbe3-149c-4bab-9b13-b92eca8744f0)


## # Отображение всех заказов

### Получаем все заказы из базы данных

![Снимок экрана 2025-03-08 070741](https://github.com/user-attachments/assets/c7f7e9e6-425a-4b4e-894b-e0bcd530ff44)

### Если нажать на ID заказа, то можно будет _отредактировать его содержимое_

![capture_250308_070911](https://github.com/user-attachments/assets/824b5bbf-5457-4161-9cd1-6eddfd8fecb7)

![Снимок экрана 2025-03-08 070925](https://github.com/user-attachments/assets/ae507be8-86c5-4e86-ada7-fb73f6de6cf3)


![Снимок экрана 2025-03-08 071122](https://github.com/user-attachments/assets/2b01ff23-da2f-4daf-b37c-9ed5e8137bbe)


![capture_250308_071158](https://github.com/user-attachments/assets/91270386-1ebe-4296-80f3-a7b53053326c)


## # Изменение статуса заказа

### Страница предоставляет возможность выбрать заказ из списка существующих, а также установить ему допустимый статус 

![Снимок экрана 2025-03-08 071330](https://github.com/user-attachments/assets/01fce1e7-a951-4793-bf36-30f8d5438a07)

### Изменим несколько заказов на статус «Оплачено» для демонстрации следующей вкладки

![Снимок экрана 2025-03-08 071507](https://github.com/user-attachments/assets/7abf8a51-50a0-4766-8968-382d768d8385)


## # Расчет выручки за смену

### На этой странице отображается общий объем выручки за заказы со статусом «Оплачено»

![Снимок экрана 2025-03-08 071632](https://github.com/user-attachments/assets/0166689b-51d2-44a8-9b93-cf6766fe366f)


### А вот по каким заказам шёл расчёт


![capture_250308_071855](https://github.com/user-attachments/assets/fc7f3638-7db9-48c5-8130-c9a41a38288e)


# Обзор функционала приложения через API.

## Все возможности, которые доступны через веб-интерфейс, также реализованы через API

![Снимок экрана 2025-03-08 072223](https://github.com/user-attachments/assets/c33eefd5-72c1-424e-81d3-b65753186ed7)


## # Создание заказа

![Снимок экрана 2025-03-08 072753](https://github.com/user-attachments/assets/353b7dba-c347-44ab-9cdf-e90c6107a98c)


### С валидацией, само собой

![Снимок экрана 2025-03-08 072808](https://github.com/user-attachments/assets/5b4b36bb-c64b-46a2-9dc6-9c18e29e577a)

![Снимок экрана 2025-03-08 072816](https://github.com/user-attachments/assets/c3873841-8db4-4360-930e-562cbfc83d7b)

### Создадим несколько заказов для обзора остального функционала

![Снимок экрана 2025-03-08 072952](https://github.com/user-attachments/assets/b65fb5db-f51b-42d7-b437-7a4fd36d57ed)

![Снимок экрана 2025-03-08 073001](https://github.com/user-attachments/assets/678c3224-7a6d-4d7e-b2d6-846b26a307c5)

## # Получение списка заказов: _/api/v1/order_list/_

![Снимок экрана 2025-03-08 073400](https://github.com/user-attachments/assets/66c2159c-fd2a-4ee4-922f-8a76d5c40134)

## URL также поддерживает фильтрацию либо по статусу заказа, либо по номеру стола, например: _api/v1/order_list/?table_number=1_

![Снимок экрана 2025-03-08 073614](https://github.com/user-attachments/assets/23626bdd-722c-447b-878c-3a681a03370e)




