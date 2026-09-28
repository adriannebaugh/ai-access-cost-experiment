public with sharing class PetExperimentController {
    @AuraEnabled(cacheable=true)
    public static List<PetExperimentPet> getPublicPets() {
        List<Pet__c> pets = [
            SELECT Id, Name, Species__c, Breed__c, Age__c, Status__c,
                   Energy__c, Chaos__c, Behavior_Risk__c, Good_With_Kids__c,
                   (SELECT Application_Count__c
                    FROM Application_Summaries__r
                    WHERE Publicly_Displayed__c = true
                    ORDER BY CreatedDate DESC
                    LIMIT 1)
            FROM Pet__c
            WHERE Publicly_Displayed__c = true
            ORDER BY Name
            LIMIT 100
        ];

        List<PetExperimentPet> results = new List<PetExperimentPet>();
        for (Pet__c pet : pets) {
            Decimal applicationCount = 0;
            if (!pet.Application_Summaries__r.isEmpty()) {
                applicationCount = pet.Application_Summaries__r[0].Application_Count__c;
            }
            results.add(new PetExperimentPet(pet, applicationCount));
        }
        return results;
    }
}