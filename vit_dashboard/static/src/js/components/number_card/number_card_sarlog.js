/** @odoo-module **/
const { Component, onMounted, onWillDestroy, useState } = owl;
import { useService } from "@web/core/utils/hooks";

export class NumberCardSarlog extends Component {
    static template = "vit_dashboard.NumberCardSarlog";
    static props = {
        title: { type: String },
        bgColor: { type: String, optional: true },
        icon: { type: String, optional: true },
        model: { type: String, optional: true },
        field: { type: String, optional: true },
        domain: { type: Array, optional: true },
        data: { type: Object, optional: true },
    };


    setup() {
        this.orm = useService("orm");

        this.state = useState({
            val: { master_list: [] },
        });

        onMounted(async () => {
            await this.reload();
        });

        onWillDestroy(() => {
            this.isDestroyed = true;
        });
    }

    async reload() {
        try {
            const result = await this.orm.call(
                this.props.model,
                "get_statistics_sarlog", 
                []
            );

            this.state.val = result || { master_list: [] };
        } catch (error) {
            console.error("❌ Error loading NumberCardSarlog:", error);
            this.state.val = { master_list: [] };
        }
    }
}
