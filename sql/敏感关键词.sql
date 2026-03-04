SELECT 
    id,
    sender_name,
    date_sent,
    content_text,
    -- 标记检测到的隐私类型
    CASE 
        WHEN content_text REGEXP '1[3-9][0-9]{9}' THEN '手机号'
        WHEN content_text REGEXP '[1-9][0-9]{16}[0-9xX]' THEN '身份证号'
        WHEN content_text REGEXP '(62|60|4[0-9])[0-9]{13,17}' THEN '银行卡号'
        WHEN content_text REGEXP 'T[A-Za-z0-9]{33}' THEN 'USDT-TRC20地址'
        WHEN content_text REGEXP '0x[a-fA-F0-9]{40}' THEN 'ETH/BSC地址'
        WHEN content_text REGEXP '[1-9][0-9]{4,11}' AND content_text LIKE '%QQ%' THEN 'QQ号'
        WHEN content_text REGEXP '姓名|实名|电话|地址|密码|支付宝|微信|卡号' THEN '敏感关键词'
        ELSE '其他潜在信息'
    END AS potential_privacy_type,
		source_file AS `来源`
FROM 
    tg_messages
WHERE 
    -- 1. 匹配中国大陆手机号 (1开头，第二位3-9，共11位)
    content_text REGEXP '1[3-9][0-9]{9}' 
    
    -- 2. 匹配身份证号 (18位，最后一位可能是X)
    OR content_text REGEXP '[1-9][0-9]{16}[0-9xX]'
    
    -- 3. 匹配常见银行卡号 (16-19位数字，通常以6, 5, 4开头)
    OR content_text REGEXP '(62|60|4[0-9]|5[0-9])[0-9]{13,17}'
    
    -- 4. 匹配虚拟货币地址 (TRC20以T开头34位, ETH以0x开头42位)
    OR content_text REGEXP 'T[A-Za-z0-9]{33}'
    OR content_text REGEXP '0x[a-fA-F0-9]{40}'
    
    -- 5. 匹配包含特定敏感词的记录
    OR content_text REGEXP '姓名|真实姓名|电话|手机号|身份证|银行卡|卡号|支付宝|微信|QQ|地址|密码|私钥|助记词'
    
    -- 6. 匹配疑似QQ号或ID (5-12位数字，需结合上下文，这里作为宽泛筛选)
    OR (content_text REGEXP '[1-9][0-9]{5,10}' AND (content_text LIKE '%QQ%' OR content_text LIKE '%号%'))

ORDER BY 
    date_sent DESC;