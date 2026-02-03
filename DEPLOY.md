# Развертывание бота на VPS

## Требования

- VPS с Ubuntu 20.04+ (рекомендуется Ubuntu 22.04)
- Минимум 512MB RAM (рекомендуется 1GB)
- Python 3.8+
- SSH доступ к серверу

## Пошаговая инструкция

### 1. Подключение к VPS

```bash
ssh your_username@your_server_ip
```

### 2. Обновление системы

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Установка Python и необходимых пакетов

```bash
sudo apt install python3 python3-pip python3-venv git -y
```

### 4. Создание директории для бота

```bash
mkdir ~/budget_bot
cd ~/budget_bot
```

### 5. Загрузка файлов проекта

**Вариант A: Через Git (рекомендуется)**
```bash
git clone your_repository_url .
```

**Вариант B: Через SCP (с локального компьютера)**
```bash
# На вашем локальном компьютере:
scp -r c:\Users\Alisher\Documents\gen_plan\budget_bot/* your_username@your_server_ip:~/budget_bot/
```

### 6. Создание виртуального окружения

```bash
cd ~/budget_bot
python3 -m venv venv
source venv/bin/activate
```

### 7. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 8. Настройка переменных окружения

```bash
# Создайте файл .env
nano .env
```

Добавьте в файл:
```
BOT_TOKEN=ваш_токен_бота
```

Сохраните (Ctrl+O, Enter, Ctrl+X)

### 9. Проверка запуска

```bash
python main.py
```

Если бот запустился успешно, остановите его (Ctrl+C) и переходите к настройке автозапуска.

### 10. Настройка автозапуска через systemd

#### 10.1. Отредактируйте файл сервиса

```bash
nano budget_bot.service
```

Замените `YOUR_USERNAME` на ваше имя пользователя в Linux (узнать можно командой `whoami`).

#### 10.2. Скопируйте файл сервиса

```bash
sudo cp budget_bot.service /etc/systemd/system/
```

#### 10.3. Перезагрузите systemd и запустите сервис

```bash
sudo systemctl daemon-reload
sudo systemctl enable budget_bot.service
sudo systemctl start budget_bot.service
```

#### 10.4. Проверьте статус

```bash
sudo systemctl status budget_bot.service
```

Должно быть: `Active: active (running)`

### 11. Полезные команды

**Просмотр логов:**
```bash
sudo journalctl -u budget_bot.service -f
```

**Остановка бота:**
```bash
sudo systemctl stop budget_bot.service
```

**Перезапуск бота:**
```bash
sudo systemctl restart budget_bot.service
```

**Отключить автозапуск:**
```bash
sudo systemctl disable budget_bot.service
```

## Обновление бота

### Через Git:
```bash
cd ~/budget_bot
git pull
sudo systemctl restart budget_bot.service
```

### Вручную:
```bash
# Загрузите новые файлы через SCP
sudo systemctl restart budget_bot.service
```

## Безопасность

### 1. Настройка файрвола

```bash
sudo apt install ufw -y
sudo ufw allow ssh
sudo ufw allow 22/tcp
sudo ufw enable
```

### 2. Создание отдельного пользователя для бота (рекомендуется)

```bash
sudo adduser botuser
sudo su - botuser
# Повторите шаги 4-10 от имени этого пользователя
```

### 3. Защита файла .env

```bash
chmod 600 .env
```

## Мониторинг

### Проверка использования ресурсов:
```bash
htop
```

### Проверка места на диске:
```bash
df -h
```

### Размер базы данных:
```bash
du -h budget_bot.db
```

## Резервное копирование

### Создание резервной копии базы данных:
```bash
cp budget_bot.db budget_bot_backup_$(date +%Y%m%d).db
```

### Автоматическое резервное копирование (cron):
```bash
crontab -e
```

Добавьте строку (ежедневный бэкап в 3:00 ночи):
```
0 3 * * * cp ~/budget_bot/budget_bot.db ~/budget_bot/backups/budget_bot_$(date +\%Y\%m\%d).db
```

Создайте папку для бэкапов:
```bash
mkdir ~/budget_bot/backups
```

## Рекомендуемые VPS провайдеры

1. **DigitalOcean** - $5/месяц (1GB RAM, 25GB SSD)
   - Простой интерфейс
   - Хорошая документация
   - [Ссылка с $200 кредитом на 60 дней](https://www.digitalocean.com)

2. **Hetzner** - от €4/месяц
   - Дешевле чем DigitalOcean
   - Европейские датацентры
   - Отличная производительность

3. **Vultr** - $5/месяц
   - Много локаций серверов
   - Почасовая оплата

4. **Contabo** - от €4/месяц
   - Очень дешево
   - Больше ресурсов за деньги

## Устранение неполадок

### Бот не запускается:
```bash
# Проверьте логи
sudo journalctl -u budget_bot.service -n 50

# Проверьте, установлены ли зависимости
source ~/budget_bot/venv/bin/activate
pip list

# Проверьте права доступа
ls -la ~/budget_bot/
```

### База данных заблокирована:
```bash
# Убедитесь, что бот запущен только в одном экземпляре
ps aux | grep python
```

### Недостаточно памяти:
```bash
# Проверьте использование памяти
free -h

# Создайте swap файл (если нет)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Поддержка

Если возникли проблемы, проверьте:
1. Логи сервиса: `sudo journalctl -u budget_bot.service -f`
2. Правильность токена в .env файле
3. Доступ к интернету: `ping telegram.org`
