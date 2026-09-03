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
            this.state.rows = result.rows || [];
            this.state.totals = result.totals || {};
            this.state.title = result.title || "";
        } finally {
            this.state.isLoading = false;
        }
    }

    async onMasterBudgetChange(ev) {
        this.state.selectedMasterBudgetId = ev.target.value ? parseInt(ev.target.value) : null;
        await this.loadDashboard();
    }

    async onYearChange(ev) {
        this.state.selectedYear = ev.target.value ? parseInt(ev.target.value) : new Date().getFullYear();
        await this.loadDashboard();
    }
}

SarlogKanwilDashboard.template = "vit_dashboard.SarlogKanwilDashboard";

registry.category("actions").add("vit_dashboard.SarlogKanwilDashboard", SarlogKanwilDashboard);
