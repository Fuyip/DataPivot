TRUNCATE TABLE bank_all_statements_with_info;
INSERT INTO bank_all_statements_with_info
SELECT
*
FROM
bank_all_statements
WHERE
(
ip_loc IS NOT NULL
OR
mac_loc IS NOT NULL
) AND NOT (
ip_loc =''
AND
mac_loc =''
)