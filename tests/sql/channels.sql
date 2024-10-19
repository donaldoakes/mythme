SELECT chanid, channum, callsign, name, icon
FROM channel
WHERE visible = 1
AND DELETED is NULL
ORDER BY CONVERT(channum, UNSIGNED) asc;

