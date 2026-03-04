SELECT
`姓名`,
`身份证号码`,
GROUP_CONCAT(DISTINCT CONCAT(来源姓名,'-',来源身份证)),
COUNT(DISTINCT CONCAT(来源姓名,'-',来源身份证))
FROM
`云搜综合分析`
GROUP BY
`身份证号码`
ORDER BY COUNT(DISTINCT CONCAT(来源姓名,'-',来源身份证)) DESC
