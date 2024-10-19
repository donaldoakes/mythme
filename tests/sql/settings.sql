SELECT value, data, hostname
FROM settings
WHERE value in ('BackendStatusPort', 'BackendServerAddr')