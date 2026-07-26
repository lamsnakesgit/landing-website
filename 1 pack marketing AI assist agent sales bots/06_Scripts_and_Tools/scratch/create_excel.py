import pandas as pd
import datetime as dt

# 1. Загрузка данных
df = pd.read_csv('cv_hunt_career/CRM_marketer/dataset_crm.csv', on_bad_lines='skip')
if df.columns[0].startswith('Unnamed'):
    df = df.iloc[:, 1:]

df['Дата покупки'] = pd.to_datetime(df['Дата покупки'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
df = df.dropna(subset=['Дата покупки', 'Контакт', 'Сумма'])

# 2. Создаем сводную таблицу (RFM)
current_date = df['Дата покупки'].max() + dt.timedelta(days=1)

rfm = df.groupby('Контакт').agg({
    'Дата покупки': lambda x: (current_date - x.max()).days,
    'Карта': 'count',
    'Сумма': 'sum'
}).rename(columns={
    'Дата покупки': 'Recency (Дней с последней покупки)', 
    'Карта': 'Frequency (Количество покупок)', 
    'Сумма': 'Monetary (Общая сумма покупок)'
})

rfm['Avg_Check (Средний чек)'] = rfm['Monetary (Общая сумма покупок)'] / rfm['Frequency (Количество покупок)']

# 3. Достаем реальные сегменты (без масштабирования)
q75_m = rfm['Monetary (Общая сумма покупок)'].quantile(0.75)
seg1 = rfm[(rfm['Recency (Дней с последней покупки)'] > 180) & (rfm['Frequency (Количество покупок)'] >= 2) & (rfm['Monetary (Общая сумма покупок)'] >= q75_m)]

q75_avg = rfm['Avg_Check (Средний чек)'].quantile(0.75)
seg2 = rfm[(rfm['Frequency (Количество покупок)'] == 1) & (rfm['Recency (Дней с последней покупки)'] <= 180) & (rfm['Monetary (Общая сумма покупок)'] >= q75_avg)]

q25_m = rfm['Monetary (Общая сумма покупок)'].quantile(0.25)
seg3 = rfm[(rfm['Frequency (Количество покупок)'] <= 2) & (rfm['Recency (Дней с последней покупки)'] > 90) & (rfm['Recency (Дней с последней покупки)'] <= 365) & (rfm['Monetary (Общая сумма покупок)'] >= q25_m) & (rfm['Monetary (Общая сумма покупок)'] < q75_m)]

# 4. Сохраняем в красивый Excel
file_path = 'cv_hunt_career/CRM_marketer/RFM_Analysis_Intertop.xlsx'
with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='1. Сырые данные', index=False)
    rfm.to_excel(writer, sheet_name='2. RFM Сводная таблица')
    seg1.to_excel(writer, sheet_name='3. Сегмент Отток VIP')
    seg2.to_excel(writer, sheet_name='4. Сегмент Новички')
    seg3.to_excel(writer, sheet_name='5. Сегмент Спящие середняки')

print("Excel файл успешно создан!")
