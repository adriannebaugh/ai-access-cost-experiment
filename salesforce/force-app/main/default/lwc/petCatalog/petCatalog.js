import { LightningElement, wire } from 'lwc';
import getPublicPets from '@salesforce/apex/PetExperimentController.getPublicPets';

const STATUS_OPTIONS = [
    { label: 'All statuses', value: 'All' },
    { label: 'Available', value: 'Available' },
    { label: 'Pending', value: 'Pending' },
    { label: 'Adopted', value: 'Adopted' }
];

const SORT_OPTIONS = [
    { label: 'Name', value: 'name' },
    { label: 'Most chaos', value: 'chaos' },
    { label: 'Most applications', value: 'applications' }
];

export default class PetCatalog extends LightningElement {
    pets = [];
    searchTerm = '';
    statusFilter = 'All';
    sortBy = 'name';
    isLoading = true;
    errorMessage = '';

    @wire(getPublicPets)
    wiredPets({ data, error }) {
        if (data) {
            this.pets = data.map((pet) => ({
                ...pet,
                statusClass: `status-pill ${pet.status.toLowerCase()}`,
                chaosClass: pet.chaos >= 9 ? 'meter-fill high' : 'meter-fill',
                chaosStyle: `width: ${Math.max(0, Math.min(100, pet.chaos * 10))}%`
            }));
            this.errorMessage = '';
            this.isLoading = false;
        } else if (error) {
            this.errorMessage = 'The public roster is temporarily unavailable.';
            this.isLoading = false;
        }
    }

    get statusOptions() {
        return STATUS_OPTIONS;
    }

    get sortOptions() {
        return SORT_OPTIONS;
    }

    get totalCount() {
        return this.pets.length;
    }

    get availableCount() {
        return this.pets.filter((pet) => pet.status === 'Available').length;
    }

    get highChaosCount() {
        return this.pets.filter((pet) => pet.chaos >= 9).length;
    }

    get applicationTotal() {
        return this.pets.reduce((total, pet) => total + pet.applicationCount, 0);
    }

    get visiblePets() {
        const query = this.searchTerm.trim().toLowerCase();
        const filtered = this.pets.filter((pet) => {
            const matchesStatus = this.statusFilter === 'All' || pet.status === this.statusFilter;
            const matchesSearch = !query || `${pet.name} ${pet.species} ${pet.breed}`.toLowerCase().includes(query);
            return matchesStatus && matchesSearch;
        });

        return [...filtered].sort((first, second) => {
            if (this.sortBy === 'chaos') return second.chaos - first.chaos || first.name.localeCompare(second.name);
            if (this.sortBy === 'applications') return second.applicationCount - first.applicationCount || first.name.localeCompare(second.name);
            return first.name.localeCompare(second.name);
        });
    }

    get resultCountLabel() {
        const noun = this.visiblePets.length === 1 ? 'pet' : 'pets';
        return `${this.visiblePets.length} ${noun}`;
    }

    get hasPets() {
        return this.visiblePets.length > 0;
    }

    handleSearch(event) {
        this.searchTerm = event.detail.value;
    }

    handleStatusChange(event) {
        this.statusFilter = event.detail.value;
    }

    handleSortChange(event) {
        this.sortBy = event.detail.value;
    }
}