/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const { Component, onWillStart, useState } = owl;

export class RkapDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        const currentYear = new Date().getFullYear();

        this.state = useState({
            isLoading: true,
            isDownloading: false,
            selectedYear: currentYear,
            availableYears: Array.from({ length: 6 }, (_, index) => currentYear - 5 + index),
            title: "",
            categories: [],
            totals: {},
        });

        onWillStart(() => this.loadDashboard());
    }

    formatAmount(value) {
        return new Intl.NumberFormat("id-ID", { maximumFractionDigits: 0 }).format(value || 0);
    }

    formatProgress(value) {
        return `${Number(value || 0).toFixed(2)}%`;
    }

    async loadDashboard() {
        this.state.isLoading = true;
        try {
            const result = await this.orm.call(
                "wizard.export.rkap.sarlog",
                "get_dashboard_data",
                [this.state.selectedYear]
            );
            this.state.title = result.title || "";
            this.state.categories = result.categories || [];
            this.state.totals = result.totals || {};
        } catch (error) {
            this.notification.add("Data Dashboard RKAP gagal dimuat.", { type: "danger" });
            throw error;
        } finally {
            this.state.isLoading = false;
        }
    }

    async onYearChange(event) {
        this.state.selectedYear = parseInt(event.target.value, 10);
        await this.loadDashboard();
    }

    async downloadDashboard() {
        if (this.state.isDownloading) {
            return;
        }
        this.state.isDownloading = true;
        try {
            const wizardIds = await this.orm.create("wizard.export.rkap.sarlog", [{
                year: String(this.state.selectedYear),
            }]);
            const downloadAction = await this.orm.call(
                "wizard.export.rkap.sarlog",
                "action_export_excel",
                [wizardIds]
            );
            await this.action.doAction(downloadAction);
        } catch (error) {
            this.notification.add("File Dashboard RKAP gagal dibuat.", { type: "danger" });
            throw error;
        } finally {
            this.state.isDownloading = false;
        }
    }
}

RkapDashboard.template = "vit_dashboard.RkapDashboard";

registry.category("actions").add("vit_dashboard.RkapDashboard", RkapDashboard);
