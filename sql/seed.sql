INSERT INTO project_templates (id, name, description) VALUES
    (1, '商場停車模板', '適用於商場類停車場'),
    (2, '醫院停車模板', '適用於醫院類停車場')
ON CONFLICT(id) DO NOTHING;

INSERT INTO template_columns (id, template_id, name, column_type, sort_order, is_active) VALUES
    (1, 1, '月租收入', 'income', 1, 1),
    (2, 1, '臨停收入', 'income', 2, 1),
    (3, 1, '人工成本', 'expense', 3, 1),
    (4, 1, '水電費', 'expense', 4, 1),
    (5, 1, '經營說明', 'text', 5, 1),
    (6, 2, '月租收入', 'income', 1, 1),
    (7, 2, '新能源充電收入', 'income', 2, 1),
    (8, 2, '保安外包費', 'expense', 3, 1),
    (9, 2, '設備維保費', 'expense', 4, 1),
    (10, 2, '備註', 'text', 5, 1)
ON CONFLICT(id) DO NOTHING;

INSERT INTO projects (id, name, region, description, template_id) VALUES
    (1, '北京朝陽廣場停車場', '北京', '商場配套地下停車場', 1),
    (2, '北京國貿寫字樓停車場', '北京', '寫字樓配套地下停車場', 1),
    (3, '蘇州濱江醫院停車場', '外地', '醫院配套地面與地下車位', 2)
ON CONFLICT(id) DO NOTHING;

INSERT INTO project_columns (id, project_id, name, column_type, sort_order, is_active) VALUES
    (1, 1, '月租收入', 'income', 1, 1),
    (2, 1, '臨停收入', 'income', 2, 1),
    (3, 1, '人工成本', 'expense', 3, 1),
    (4, 1, '水電費', 'expense', 4, 1),
    (5, 1, '經營說明', 'text', 5, 1),
    (6, 2, '月租收入', 'income', 1, 1),
    (7, 2, '臨停收入', 'income', 2, 1),
    (8, 2, '人工成本', 'expense', 3, 1),
    (9, 2, '場地租金', 'expense', 4, 1),
    (10, 2, '經營說明', 'text', 5, 1),
    (11, 3, '月租收入', 'income', 1, 1),
    (12, 3, '新能源充電收入', 'income', 2, 1),
    (13, 3, '保安外包費', 'expense', 3, 1),
    (14, 3, '設備維保費', 'expense', 4, 1),
    (15, 3, '備註', 'text', 5, 1)
ON CONFLICT(id) DO NOTHING;

INSERT INTO monthly_records (
    id, project_id, record_month, notes, total_income, total_expense, net_income
) VALUES
    (1, 1, '2026-01', '春節前客流增加', 150000, 47000, 103000),
    (2, 1, '2026-02', '活動促銷後收入回落', 138000, 45000, 93000),
    (3, 2, '2026-01', '寫字樓復工後車流穩定', 132000, 68000, 64000),
    (4, 2, '2026-02', '招商活動增加臨停', 141000, 70000, 71000),
    (5, 3, '2026-01', '新增充電區投入運營', 118000, 39000, 79000),
    (6, 3, '2026-02', '住院流量增加', 125000, 41000, 84000)
ON CONFLICT(id) DO NOTHING;

INSERT INTO monthly_record_values (monthly_record_id, column_id, value_text) VALUES
    (1, 1, '90000.00'),
    (1, 2, '60000.00'),
    (1, 3, '32000.00'),
    (1, 4, '15000.00'),
    (1, 5, '商場活動帶動週末車流'),
    (2, 1, '85000.00'),
    (2, 2, '53000.00'),
    (2, 3, '30000.00'),
    (2, 4, '15000.00'),
    (2, 5, '節後客流較一月回落'),
    (3, 6, '86000.00'),
    (3, 7, '46000.00'),
    (3, 8, '28000.00'),
    (3, 9, '40000.00'),
    (3, 10, '周邊商務客群較穩定'),
    (4, 6, '88000.00'),
    (4, 7, '53000.00'),
    (4, 8, '30000.00'),
    (4, 9, '40000.00'),
    (4, 10, '招商活動帶動短時停車'),
    (5, 11, '70000.00'),
    (5, 12, '48000.00'),
    (5, 13, '26000.00'),
    (5, 14, '13000.00'),
    (5, 15, '充電樁上線首月表現良好'),
    (6, 11, '74000.00'),
    (6, 12, '51000.00'),
    (6, 13, '27000.00'),
    (6, 14, '14000.00'),
    (6, 15, '醫院住院人流帶動收入')
ON CONFLICT(monthly_record_id, column_id) DO NOTHING;
