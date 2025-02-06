WITH max_goals AS (
    SELECT 
        team_id, 
        MAX(goals) AS max_goals
    FROM 
        player_stats
    where player_stats.goals > 0
    GROUP BY 
        team_id
)

SELECT 
    player_stats.player_name, 
    player_stats.goals, 
    player_stats.team_name
FROM 
    player_stats 
JOIN 
    max_goals mg ON player_stats.team_id = mg.team_id AND player_stats.goals = mg.max_goals
ORDER BY 
    max_goals DESC