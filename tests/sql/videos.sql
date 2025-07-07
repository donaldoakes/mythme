SELECT * FROM videometadata where intid in (53170, 52656)

DELETE FROM videometadatacast

INSERT INTO videometadata
(host, filename, title, hash, contenttype,
year, releasedate, userrating, inetref, coverfile, director,
subtitle, collectionref, homepage, rating, length, playcount, season, episode, showlevel, childid, browse, watched, processed, category)
VALUES
('fedora', '1980s/Gen X/My Hot Video - Gen X.ts', 'My Hot Video - Gen X', 'abcdef123455', 'MUSICVIDEO',
0, '0000-00-00', 0, '00000000', '', '',
'', -1, '', 'NR', 0, 0, 0, 0, 0, -1, 1, 0, 0, 0)