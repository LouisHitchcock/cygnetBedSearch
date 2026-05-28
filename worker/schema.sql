-- Cloudflare D1 schema for Cygnet Bed Search

CREATE TABLE IF NOT EXISTS bed_data (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  name    TEXT NOT NULL,
  sex     TEXT NOT NULL,
  beds    INTEGER NOT NULL,
  purpose TEXT NOT NULL,
  date    TEXT NOT NULL,
  time    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bed_data_date ON bed_data(date);
CREATE INDEX IF NOT EXISTS idx_bed_data_name_purpose ON bed_data(name, purpose);
