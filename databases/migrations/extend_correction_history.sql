ALTER TABLE correction_history ADD COLUMN violation_code TEXT;
ALTER TABLE correction_history ADD COLUMN original_line TEXT;
ALTER TABLE correction_history ADD COLUMN corrected_line TEXT;
ALTER TABLE correction_history ADD COLUMN correction_timestamp TEXT;
