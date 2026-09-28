@IsTest
private class PetExperimentControllerTest {
    @IsTest
    static void returnsOnlyPublicPetsAndTheirPublicSummary() {
        Pet__c publicPet = new Pet__c(
            Name = 'Synthetic Public Pet',
            Species__c = 'Dog',
            Breed__c = 'Mix',
            Age__c = 3,
            Status__c = 'Available',
            Energy__c = 'Medium',
            Chaos__c = 2,
            Behavior_Risk__c = 5,
            Good_With_Kids__c = 'Yes',
            Publicly_Displayed__c = true
        );
        Pet__c privatePet = new Pet__c(
            Name = 'Synthetic Private Pet',
            Species__c = 'Cat',
            Breed__c = 'Mix',
            Age__c = 4,
            Status__c = 'Available',
            Energy__c = 'Low',
            Chaos__c = 1,
            Behavior_Risk__c = 2,
            Good_With_Kids__c = 'Maybe',
            Publicly_Displayed__c = false
        );
        insert new List<Pet__c>{ publicPet, privatePet };
        insert new Application_Summary__c(
            Pet__c = publicPet.Id,
            Application_Count__c = 7,
            Publicly_Displayed__c = true
        );

        Test.startTest();
        List<PetExperimentPet> results = PetExperimentController.getPublicPets();
        Test.stopTest();

        System.assertEquals(1, results.size());
        System.assertEquals('Synthetic Public Pet', results[0].name);
        System.assertEquals(7, results[0].applicationCount);
    }
}