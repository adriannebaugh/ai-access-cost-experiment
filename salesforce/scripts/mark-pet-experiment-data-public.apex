Set<String> sampleNames = new Set<String>{
    'Sir Barksalot III', 'Chairman Meow', 'Dumpster Fire', 'Kevin', 'Lasagna',
    'Tax Fraud', 'Princess Murdermittens', 'Gary', 'Potato Supreme',
    'Beef Wellington', 'Reverend Bitey', 'Crouton', 'Wi-Fi Password',
    'Linda from Accounting', 'Meatball'
};

List<Pet__c> pets = [
    SELECT Id, Publicly_Displayed__c
    FROM Pet__c
    WHERE Name IN :sampleNames
];
System.assertEquals(15, pets.size(), 'Expected exactly 15 synthetic pets.');

Set<Id> petIds = new Map<Id, Pet__c>(pets).keySet();
List<Application_Summary__c> summaries = [
    SELECT Id, Publicly_Displayed__c
    FROM Application_Summary__c
    WHERE Pet__c IN :petIds
];
System.assertEquals(15, summaries.size(), 'Expected exactly 15 synthetic summaries.');

for (Pet__c pet : pets) pet.Publicly_Displayed__c = true;
for (Application_Summary__c summary : summaries) summary.Publicly_Displayed__c = true;
update pets;
update summaries;