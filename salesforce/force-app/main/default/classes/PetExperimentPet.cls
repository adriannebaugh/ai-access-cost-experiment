public class PetExperimentPet {
    @AuraEnabled public String id { get; set; }
    @AuraEnabled public String name { get; set; }
    @AuraEnabled public String species { get; set; }
    @AuraEnabled public String breed { get; set; }
    @AuraEnabled public Decimal age { get; set; }
    @AuraEnabled public String status { get; set; }
    @AuraEnabled public String energy { get; set; }
    @AuraEnabled public Decimal chaos { get; set; }
    @AuraEnabled public Decimal behaviorRisk { get; set; }
    @AuraEnabled public String goodWithKids { get; set; }
    @AuraEnabled public Decimal applicationCount { get; set; }

    public PetExperimentPet(Pet__c pet, Decimal count) {
        id = pet.Id;
        name = pet.Name;
        species = pet.Species__c;
        breed = pet.Breed__c;
        age = pet.Age__c;
        status = pet.Status__c;
        energy = pet.Energy__c;
        chaos = pet.Chaos__c;
        behaviorRisk = pet.Behavior_Risk__c;
        goodWithKids = pet.Good_With_Kids__c;
        applicationCount = count;
    }
}