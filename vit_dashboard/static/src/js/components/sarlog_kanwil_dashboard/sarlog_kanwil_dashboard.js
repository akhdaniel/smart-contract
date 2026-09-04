/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, onWillStart, useState } = owl;

export class SarlogKanwilDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        const currentYear = new Date().getFullYear();

        this.state = useState({
            isLoading: true,
            selectedYear: currentYear,
            selectedMasterBudgetId: null,
            masterBudgetSearchText: "",
            masterBudgetManuallySelected: false,
            masterBudgetDropdownOpen: false,
            masterBudgetDropdownShowAll: false,
            availableYears: Array.from({ length: 6 }, (_, i) => currentYear - 5 + i),
            masterBudgets: [],
            rows: [],
            totals: {},
            title: "",
        });

        onWillStart(async () => {
            await this.loadDashboard();
        });
    }

    async loadDashboard() {
        this.state.isLoading = true;
        try {
            const result = await this.orm.call(
                "vit.budget_rkap",
                "get_sarlog_kanwil_dashboard",
                [this.state.selectedMasterBudgetId, this.state.selectedYear]
            );
            this.state.masterBudgets = result.master_budgets || [];
            this.state.selectedMasterBudgetId = result.selected_master_budget_id || null;
            this.state.masterBudgetSearchText = this.state.masterBudgetManuallySelected
                ? this.getSelectedMasterBudgetName()
                : "";
            this.state.rows = result.rows || [];
            this.state.totals = result.totals || {};
            this.state.title = result.title || "";
        } finally {
            this.state.isLoading = false;
        }
    }

    getSelectedMasterBudgetName() {
        const selected = this.state.masterBudgets.find(
            (mb) => mb.id === this.state.selectedMasterBudgetId
        );
        return selected ? selected.name : "";
    }

    get filteredMasterBudgets() {
        if (this.state.masterBudgetDropdownShowAll) {
            return this.state.masterBudgets;
        }
        const query = (this.state.masterBudgetSearchText || "").toLowerCase();
        if (!query) {
            return this.state.masterBudgets;
        }
        return this.state.masterBudgets.filter((mb) => mb.name.toLowerCase().includes(query));
    }

    async onMasterBudgetInput(ev) {
        const value = ev.target.value || "";
        this.state.masterBudgetSearchText = value;
        this.state.masterBudgetDropdownOpen = true;
        this.state.masterBudgetDropdownShowAll = false;

        if (!value) {
            this.state.selectedMasterBudgetId = null;
            this.state.masterBudgetManuallySelected = false;
            await this.loadDashboard();
            return;
        }

        const selected = this.state.masterBudgets.find(
            (mb) => mb.name.toLowerCase() === value.toLowerCase()
        );
        if (selected && selected.id !== this.state.selectedMasterBudgetId) {
            this.state.selectedMasterBudgetId = selected.id;
            this.state.masterBudgetManuallySelected = true;
            await this.loadDashboard();
        }
    }

    onMasterBudgetFocus() {
        this.state.masterBudgetDropdownOpen = true;
        this.state.masterBudgetDropdownShowAll = false;
    }

    onMasterBudgetToggleDropdown() {
        this.state.masterBudgetDropdownOpen = !this.state.masterBudgetDropdownOpen;
        this.state.masterBudgetDropdownShowAll = true;
    }

    closeMasterBudgetDropdown() {
        setTimeout(() => {
            this.state.masterBudgetDropdownOpen = false;
            this.state.masterBudgetDropdownShowAll = false;
        }, 150);
    }

    async selectMasterBudget(mb) {
        this.state.selectedMasterBudgetId = mb.id;
        this.state.masterBudgetManuallySelected = true;
        this.state.masterBudgetSearchText = mb.name;
        this.state.masterBudgetDropdownOpen = false;
        this.state.masterBudgetDropdownShowAll = false;
        await this.loadDashboard();
    }

    async selectMasterBudgetFromEvent(ev) {
        const selectedId = parseInt(ev.currentTarget.dataset.id);
        const selected = this.state.masterBudgets.find((mb) => mb.id === selectedId);
        if (selected) {
            await this.selectMasterBudget(selected);
        }
    }

    async onYearChange(ev) {
        this.state.selectedYear = ev.target.value ? parseInt(ev.target.value) : new Date().getFullYear();
        await this.loadDashboard();
    }
}

SarlogKanwilDashboard.template = "vit_dashboard.SarlogKanwilDashboard";

registry.category("actions").add("vit_dashboard.SarlogKanwilDashboard", SarlogKanwilDashboard);
