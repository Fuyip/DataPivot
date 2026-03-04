SELECT
DISTINCT
主体微信号
FROM
`29-微信好友` w
LEFT JOIN(
SELECT
DISTINCT
账号
FROM
`人员总体归纳`
)t1 ON t1.`账号`=w.`主体微信号`
WHERE
t1.`账号` IS NULL;
UPDATE
`29-微信好友` w
INNER JOIN(
SELECT
*
FROM
id_exg_zh
)t1 ON w.主体微信号=t1.微信id
SET w.`主体微信号`=t1.微信号