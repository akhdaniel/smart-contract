/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, useState } = owl;
import { NumberCardSarlog } from "../number_card/number_card_sarlog";

export class SarlogDashboard extends Component {
    setup() {
        console.log("SarlogDashboard...");
        this.orm = useService("orm");

        this.state = useState({
            masterBudgets: [],
            totalSummary: {},
        });

        onWillStart(async () => {
            const result = await this.orm.call(
                "vit.budget_rkap",
                "get_statistics_sarlog",
                []
            );

            this.state.masterBudgets = result.master_list || [];

            this.state.totalSummary = result.total_summary || {};
        });
    }
}

SarlogDashboard.template = "vit_dashboard.SarlogDashboard";
SarlogDashboard.components = { NumberCardSarlog };

registry.category("actions").add("vit_dashboard.SarlogDashboard", SarlogDashboard);
