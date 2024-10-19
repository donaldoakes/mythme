SELECT channel.chanid, channel.channum, channel.callsign, channel.name, channel.visible,
program.title, program.subtitle, program.starttime, program.endtime, program.description, program.category, program.category_type, CONVERT(program.airdate USING utf8), program.stars, program.season, program.episode
FROM channel, program
WHERE channel.chanid = program.chanid
AND program.starttime >= NOW()
ORDER BY starttime asc
LIMIT 100 OFFSET 101

SELECT @@global.time_zone, @@session.time_zone;

SELECT channel.chanid, channel.channum, channel.callsign, channel.name,
program.title, program.subtitle, program.starttime, program.endtime, program.description, program.category, program.category_type, CONVERT(program.airdate USING utf8), program.stars, program.season, program.episode, program.originalairdate
FROM channel, program
WHERE channel.chanid = program.chanid
AND program.endtime >= '2024-07-20T18:09:53.000Z' AND channum IN (653)
AND program.starttime >= "2024-07-21T02:00:00.000Z"
AND program.endtime < "2024-07-21T06:00:30.000Z"
ORDER BY starttime asc
LIMIT 100 OFFSET 0

select distinct(genre) from programgenres order by genre;


SELECT channel.chanid, channel.channum, channel.callsign, channel.name, channel.icon,
program.title, program.subtitle, program.starttime, program.endtime, program.description, program.category, program.category_type, CONVERT(program.airdate USING utf8), program.stars, program.season, program.episode, program.originalairdate,
(SELECT COUNT(*) FROM credits WHERE credits.chanid = program.chanid AND credits.starttime = program.starttime) AS credits
FROM channel, program
WHERE channel.chanid = program.chanid AND channel.visible > 0
AND program.endtime >= '2024-08-17T19:56:17+00:00.000Z' AND airdate = 10
ORDER BY starttime asc
LIMIT 50 OFFSET 0


select title, airdate from program
where program.endtime >= '2024-08-17T19:56:17+00:00.000Z' AND airdate = 10

-- all movies with genres
SELECT channel.chanid, channel.channum, channel.callsign, channel.name, channel.icon,
program.title, program.subtitle, program.starttime, program.endtime, program.description, program.category, program.category_type,
CONVERT(program.airdate USING utf8) as year, program.stars, program.season, program.episode, program.originalairdate, programgenres.genre,
(SELECT COUNT(*) FROM credits WHERE credits.chanid = program.chanid AND credits.starttime = program.starttime) AS credits
FROM channel, program, programgenres
WHERE channel.chanid = program.chanid AND channel.visible > 0
AND programgenres.chanid = program.chanid AND programgenres.starttime = program.starttime AND programgenres.relevance != 0
AND program.endtime >= '2024-08-18T09:04:22+00:00.000Z' AND category_type = 'movie'
ORDER BY starttime asc
LIMIT 50 OFFSET 0

-- genres
SELECT DISTINCT(programgenres.genre)
FROM programgenres
WHERE programgenres.relevance != 0