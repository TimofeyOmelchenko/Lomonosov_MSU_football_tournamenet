import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('teams_MSU4.db') 

sql_query = 'SELECT team_name, goals FROM player_stats'
df = pd.read_sql_query(sql_query, conn)

result = df.groupby('team_name').agg({'goals': 'sum'}).reset_index()

result = result.sort_values(by='goals', ascending=False)

print(result)
conn.close()

# Построение столбчатой диаграммы
ax = result.plot.bar(x='team_name', y='goals', title='Total Goals by Team', legend=False)

ax.set_xlabel('Команда')  # Метка оси X
ax.set_ylabel('Общее количество голов')  # Метка оси Y
ax.set_title('Общее количество голов по командам')  # Заголовок графика

# Настройка подписей меток осей
ax.set_xticklabels(result['team_name'], rotation=45, ha='right')  # Поворот меток на оси X
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))

plt.tight_layout()  # Для более аккуратного размещения всех элементов
plt.show()

plt.tight_layout()  # Для более аккуратного размещения всех элементов
plt.show()
