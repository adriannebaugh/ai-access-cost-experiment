-- Databricks notebook source
-- Synthetic local fixture for analytics preview; this is not a Salesforce extract.
-- IDs are deterministic mock keys. Views exist only for this notebook session.
-- COMMAND ----------
CREATE OR REPLACE TEMP VIEW sf_pet__c AS
SELECT * FROM VALUES
  ('PET-001', 'Sir Barksalot III', 'Dog', 'Corgi', 4, 'Available', 'Extreme', 8, 42, 'Yes', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-002', 'Chairman Meow', 'Cat', 'Domestic Shorthair', 7, 'Available', 'Low', 4, 18, 'Maybe', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-003', 'Dumpster Fire', 'Cat', 'Orange Tabby', 2, 'Available', 'Extreme', 10, 78, 'No', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-004', 'Kevin', 'Goat', 'Nigerian Dwarf', 3, 'Available', 'High', 10, 55, 'Yes', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-005', 'Lasagna', 'Dog', 'Basset Hound', 6, 'Pending', 'Low', 2, 10, 'Yes', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-006', 'Tax Fraud', 'Parrot', 'African Grey', 18, 'Available', 'High', 9, 61, 'Maybe', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-007', 'Princess Murdermittens', 'Cat', 'Maine Coon', 5, 'Available', 'Medium', 7, 69, 'No', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-008', 'Gary', 'Dog', 'Chihuahua Mix', 9, 'Available', 'Extreme', 9, 64, 'No', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-009', 'Potato Supreme', 'Rabbit', 'Flemish Giant', 4, 'Available', 'Low', 3, 12, 'Yes', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-010', 'Beef Wellington', 'Dog', 'English Bulldog', 5, 'Adopted', 'Low', 2, 8, 'Yes', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-011', 'Reverend Bitey', 'Cat', 'Siamese', 8, 'Available', 'Medium', 8, 73, 'No', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-012', 'Crouton', 'Dog', 'Great Dane', 2, 'Available', 'High', 7, 28, 'Yes', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-013', 'Wi-Fi Password', 'Ferret', 'Ferret', 3, 'Available', 'Extreme', 10, 47, 'Maybe', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-014', 'Linda from Accounting', 'Cat', 'Tortoiseshell', 11, 'Available', 'Low', 6, 31, 'Maybe', TIMESTAMP '2026-09-27 00:00:00', false),
  ('PET-015', 'Meatball', 'Pig', 'Mini Pig', 4, 'Available', 'Medium', 8, 36, 'Yes', TIMESTAMP '2026-09-27 00:00:00', false)
AS seed(Id, Name, Species__c, Breed__c, Age__c, Status__c, Energy__c, Chaos__c, Behavior_Risk__c, Good_With_Kids__c, SystemModstamp, IsDeleted);
-- COMMAND ----------
CREATE OR REPLACE TEMP VIEW sf_application_summary__c AS
SELECT * FROM VALUES
  ('APP-001', 'AS-0001', 'PET-001', 6, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-002', 'AS-0002', 'PET-002', 5, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-003', 'AS-0003', 'PET-003', 1, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-004', 'AS-0004', 'PET-004', 11, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-005', 'AS-0005', 'PET-005', 14, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-006', 'AS-0006', 'PET-006', 6, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-007', 'AS-0007', 'PET-007', 3, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-008', 'AS-0008', 'PET-008', 2, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-009', 'AS-0009', 'PET-009', 8, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-010', 'AS-0010', 'PET-010', 9, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-011', 'AS-0011', 'PET-011', 2, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-012', 'AS-0012', 'PET-012', 10, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-013', 'AS-0013', 'PET-013', 2, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-014', 'AS-0014', 'PET-014', 4, TIMESTAMP '2026-09-27 00:00:00', false),
  ('APP-015', 'AS-0015', 'PET-015', 7, TIMESTAMP '2026-09-27 00:00:00', false)
AS seed(Id, Name, Pet__c, Application_Count__c, SystemModstamp, IsDeleted);
-- COMMAND ----------
SELECT 'Pet__c' AS object_name, COUNT(*) AS row_count FROM sf_pet__c
UNION ALL
SELECT 'Application_Summary__c', COUNT(*) FROM sf_application_summary__c;
-- COMMAND ----------
SELECT p.Name, p.Species__c, p.Chaos__c, p.Behavior_Risk__c, a.Application_Count__c
FROM sf_pet__c p
JOIN sf_application_summary__c a ON a.Pet__c = p.Id
WHERE p.Status__c = 'Available'
  AND (p.Behavior_Risk__c >= 60 OR (p.Chaos__c >= 9 AND a.Application_Count__c <= 2))
ORDER BY p.Name;
