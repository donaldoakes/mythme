SELECT * FROM videometadata where intid in (102132)

SELECT * FROM videometadata where title = 'Strip - Adam Ant'

SELECT intid, filename FROM videometadata

DELETE FROM videometadatacast

INSERT INTO videometadata
(host, filename, title, hash, contenttype,
year, releasedate, userrating, inetref, coverfile, director,
subtitle, collectionref, homepage, rating, length, playcount, season, episode, showlevel, childid, browse, watched, processed, category)
VALUES
('fedora', '1980s/Gen X/My Hot Video - Gen X.ts', 'My Hot Video - Gen X', 'abcdef123455', 'MUSICVIDEO',
0, '0000-00-00', 0, '00000000', '', '',
'', -1, '', 'NR', 0, 0, 0, 0, 0, -1, 1, 0, 0, 0)

UPDATE videometadata WHERE filename = '1980s/Gen X/My Hot Video - Gen X.ts'
SET (host, filename, title, hash, contenttype,
year, releasedate, userrating, inetref, coverfile, director,
subtitle, collectionref, homepage, rating, length, playcount, season, episode, showlevel, childid, browse, watched, processed, category)
VALUES
('fedora', '1980s/Gen X/My Hot Video - Gen X.ts', 'My Hot Video - Gen X', 'abcdef123455', 'MUSICVIDEO',
0, '0000-00-00', 0, '00000000', '', '',
'', -1, '', 'NR', 0, 0, 0, 0, 0, -1, 1, 0, 0, 0)

INSERT INTO videocast (cast) VALUES ('somebody')

SELECT cast from videocast where intid in (select idcast from videometadatacast where idvideo = 111622)