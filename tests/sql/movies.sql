-- Active: 1720419410937@@192.168.0.70@3306@mythconverg
SELECT
channel.chanid, channel.channum, channel.callsign, channel.name,
program.title, program.subtitle, program.starttime, program.endtime, program.description, program.category, program.category_type, CONVERT(program.airdate USING utf8), program.stars, program.season, program.episode, program.originalairdate,
(SELECT COUNT(*) FROM credits WHERE credits.chanid = program.chanid AND credits.starttime = program.starttime) AS credits
FROM program, channel
WHERE channel.chanid = program.chanid
AND program.category_type='movie'
AND program.category IN ('Horror', 'Suspense', 'Mystery')
AND program.airdate BETWEEN "1930" AND "1945"
ORDER BY cast(channel.channum as unsigned), program.starttime

SELECT channel.chanid, channel.channum, channel.callsign, channel.name,
program.title, program.subtitle, program.starttime, program.endtime, program.description, program.category, program.category_type, CONVERT(program.airdate USING utf8), program.stars, program.season, program.episode, program.originalairdate
FROM channel, program
WHERE channel.chanid = program.chanid
AND channel.visible > 0
AND program.endtime >= NOW() AND title = 'American Greed'
ORDER BY starttime asc
LIMIT 100 OFFSET 0