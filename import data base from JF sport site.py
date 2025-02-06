import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3
import re

def get_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Ошибка: не удалось загрузить страницу {url}. Статус код: {response.status_code}")
        return None

def extract_goals(goals_str):
    if goals_str == '-':
        return 0
    match = re.match(r'^(\d+)', goals_str.strip())
    if match:
        return int(match.group(1))
    return None

main_url = 'https://jfsport-tournaments.join.football/tournament/1039165/teams'

main_html = get_html(main_url)

if main_html:
    main_soup = BeautifulSoup(main_html, 'html.parser')

    conn = sqlite3.connect('teams_MSU4.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DROP TABLE IF EXISTS teams')
        cursor.execute('DROP TABLE IF EXISTS player_stats')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                games INTEGER,
                goals INTEGER,
                assists INTEGER,
                yellow_cards INTEGER,
                red_cards INTEGER,
                team_id INTEGER,
                team_name TEXT,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        ''')
        
        items = main_soup.find_all('li', class_='teams__item')
        
        for item in items:
            title = item.get('title', 'No title')
            link_tag = item.find('a', class_='teams__name-link')
            
            cursor.execute('''
                INSERT INTO teams (title)
                VALUES (?)
            ''', (title,))
            team_id = cursor.lastrowid  
            
            if link_tag and 'href' in link_tag.attrs:
                team_url = urljoin(main_url, link_tag['href'])
                team_html = get_html(team_url)
                
                if team_html:
                    team_soup = BeautifulSoup(team_html, 'html.parser')
                    
                    player_rows = team_soup.find_all('tr', class_='table__row')
                    for row in player_rows:
                        player_name_tag = row.find('p', class_='table__player-name')
                        if player_name_tag:
                            player_name = player_name_tag.get_text(strip=True)
                            
                            stats_tags = row.find_all('td', class_='table__cell--variable')
                            if len(stats_tags) >= 5: 
                                games = int(stats_tags[0].get_text(strip=True)) if stats_tags[0].get_text(strip=True).isdigit() else None
                                
                                goals_str = stats_tags[1].get_text(strip=True)
                                goals = extract_goals(goals_str)
                                
                                assists = int(stats_tags[2].get_text(strip=True)) if stats_tags[2].get_text(strip=True).isdigit() else None
                                yellow_cards = int(stats_tags[3].get_text(strip=True)) if stats_tags[3].get_text(strip=True).isdigit() else None
                                red_cards = int(stats_tags[4].get_text(strip=True)) if stats_tags[4].get_text(strip=True).isdigit() else None
                                
                                cursor.execute('''
                                    INSERT INTO player_stats (player_name, games, goals, assists, yellow_cards, red_cards, team_id, team_name)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (player_name, games, goals, assists, yellow_cards, red_cards, team_id, title))
                            else:
                                print("Не удалось извлечь полную статистику игрока")
                    
                    conn.commit()
                
            else:
                print("Не удалось получить ссылку на страницу команды")
        
        conn.commit()
        print("Данные успешно сохранены в базу данных teams_MSU4.db.")
    
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
    
    finally:
        conn.close()
    
else:
    print("Не удалось получить HTML главной страницы")
