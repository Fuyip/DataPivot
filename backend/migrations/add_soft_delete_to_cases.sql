-- 为案件表添加软删除相关字段
-- 执行时间: 2026-03-04

USE datapivot;

-- 添加软删除字段
ALTER TABLE cases
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除（软删除）',
ADD COLUMN deleted_at DATETIME COMMENT '删除时间',
ADD COLUMN deleted_by INT COMMENT '删除人ID',
ADD CONSTRAINT fk_cases_deleted_by FOREIGN KEY (deleted_by) REFERENCES users(id);

-- 为已有数据设置默认值
UPDATE cases SET is_deleted = FALSE WHERE is_deleted IS NULL;

-- 添加索引以提高查询性能
CREATE INDEX idx_cases_is_deleted ON cases(is_deleted);
CREATE INDEX idx_cases_deleted_at ON cases(deleted_at);
