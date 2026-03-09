-- 创建银行信息变更申请表
-- 用于记录 bank_bin 和 sy_bank 表的变更申请和审批流程

USE datapivot;

-- 创建变更申请表
CREATE TABLE IF NOT EXISTS bank_info_change_requests (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '变更申请ID',
    table_type ENUM('bank_bin', 'sy_bank') NOT NULL COMMENT '表类型',
    change_type ENUM('create', 'update', 'delete') NOT NULL COMMENT '变更类型',

    old_data TEXT COMMENT '原始数据（JSON格式）',
    new_data TEXT NOT NULL COMMENT '新数据（JSON格式）',

    reason VARCHAR(500) COMMENT '变更原因',

    status ENUM('pending', 'approved', 'rejected', 'executed') DEFAULT 'pending' COMMENT '状态',

    created_by INT NOT NULL COMMENT '申请人ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',

    reviewed_by INT COMMENT '审批人ID',
    reviewed_at DATETIME COMMENT '审批时间',
    review_comment VARCHAR(500) COMMENT '审批意见',

    executed_at DATETIME COMMENT '执行时间',

    INDEX idx_status (status),
    INDEX idx_table_type (table_type),
    INDEX idx_created_by (created_by),
    INDEX idx_reviewed_by (reviewed_by),
    INDEX idx_created_at (created_at),

    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='银行信息变更申请表';

-- 创建索引以提高查询性能
CREATE INDEX idx_status_created_at ON bank_info_change_requests(status, created_at DESC);
CREATE INDEX idx_table_change_type ON bank_info_change_requests(table_type, change_type);
