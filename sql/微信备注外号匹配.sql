SELECT
DISTINCT
*
FROM
`29-微信好友` wxhy
INNER JOIN(
SELECT
*
FROM
`tg-外号`
)t1 ON wxhy.`好友备注` regexp t1.外号