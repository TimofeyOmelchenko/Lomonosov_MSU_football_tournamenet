WITH max_assists AS (
    SELECT 
        team_id, 
        MAX(assists) AS max_assists
    FROM 
        player_stats
    where player_stats.assists > 0
    GROUP BY 
        team_id
)

SELECT 
    player_stats.player_name, 
    player_stats.assists, 
    player_stats.team_name
FROM 
    player_stats 
JOIN 
    max_assists mg ON player_stats.team_id = mg.team_id AND player_stats.assists = mg.max_assists
ORDER BY 
    max_assists DESC