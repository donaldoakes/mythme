select distinct(role) from credits;

select people.name, credits.role, credits.priority from credits
join people on credits.person = people.person
where credits.chanid = 23914
and credits.starttime = '2024-08-01T15:30:00Z'
order by credits.priority;

SELECT COUNT(*) as credits
FROM credits
WHERE credits.chanid = 23914
AND credits.starttime = '2024-08-01T15:30:00Z'