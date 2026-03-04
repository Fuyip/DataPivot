SELECT
DISTINCT
*
FROM
pinyin_turn pt
LEFT JOIN(
SELECT
DISTINCT
*
FROM
`人员电子档案`
)t2 ON t2.姓名=pt.`中文`
LEFT JOIN(
SELECT
*
FROM
`签证表`
)t1 ON t1.`姓名`=pt.pinyin AND	t2.`出生日期`	=t1.`出生日期`
WHERE pt.`标签`='姓名'