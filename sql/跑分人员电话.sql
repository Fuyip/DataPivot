SELECT
ztqk.*,
t5.concatPhone
FROM
`3003xpj跑分卡需求` ztqk
LEFT JOIN(
SELECT
*
FROM
bank_people_info
WHERE concatPhone IS NOT NULL
GROUP BY idNum
)t5 ON t5.idNum=ztqk.`身份证号码`
