INSERT ignore INTO target_ip(ip)
SELECT
ip
FROM
iptoloc
WHERE ip
REGEXP '^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3})$';
UPDATE IGNORE target_ip
SET
label='局域网'
WHERE
ip REGEXP'^(127\\.0\\.0\\.1)|(localhost)|(10\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})|(172\\.((1[6-9])|(2\\d)|(3[01]))\\.\\d{1,3}\\.\\d{1,3})|(192\\.168\\.\\d{1,3}\\.\\d{1,3})$';
DELETE FROM target_ip
WHERE id IN(
SELECT
*
FROM(
SELECT
MAX(id)
FROM
target_ip
WHERE
label IN ('','局域网')
GROUP BY ip
HAVING COUNT(id)>1)tmp
)