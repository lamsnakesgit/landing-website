#!/bin/bash
# Скрипт автоматической подготовки VPS для Antigravity

echo "Обновление системы..."
sudo apt-get update && sudo apt-get upgrade -y

echo "Установка Node.js и npm..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "Установка Xvfb и зависимостей для графических приложений (Electron)..."
sudo apt-get install -y xvfb libnss3 libatk-bridge2.0-0 libx11-xcb1 libxcb-dri3-0 libdrm2 libgbm1 libasound2 git curl wget

echo "Установка PM2..."
sudo npm install -g pm2

echo "Клонирование Antigravity Telegram Suite..."
git clone https://github.com/emreturkmencom/antigravity-telegram-suite.git
cd antigravity-telegram-suite
npm install

echo "Создание базового .env..."
cp .env.example .env
sed -i 's/ BOT_TOKEN=.*/BOT_TOKEN=/' .env

echo "========================================================"
echo "✅ Базовая настройка сервера завершена!"
echo "Теперь тебе нужно:"
echo "1. Скачать Linux-версию Antigravity на этот сервер"
echo "2. Настроить файл .env внутри папки antigravity-telegram-suite"
echo "3. Запустить Antigravity через Xvfb и запустить бота!"
echo "========================================================"
