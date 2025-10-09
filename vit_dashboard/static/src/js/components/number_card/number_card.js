/** @odoo-module */
const { Component, onMounted, onWillDestroy, useState } = owl;
import { useService } from "@web/core/utils/hooks";

export class NumberCard extends Component {
    static template = "vit_dashboard.NumberCard";
    static props = {
        title: { type: String },
        bgColor: { type: String, optional: true },
        icon: { type: String, optional: true },
        field: { type: String, optional: true },
        model: { type: String, optional: true },
        context: { type: Object, optional: true },
        domain: { type: Object, optional: true },
        onReload: { type: Function, optional: true }, // Add onReload as an optional prop
    };

    setup() {
        this.orm = useService("orm");

        this.state = useState({
            val: { total: 0, total_aktif: 0, total_tidak_aktif: 0 },
            domain: [],
            // domainEncoded: "",
        });

        // Expose the reload method through the onReload prop
        if (this.props.onReload) {
            this.props.onReload((domain) => this.reload(domain));
        }

        onWillDestroy(() => {
            this.isDestroyed = true;
        });


        onMounted(async () => {
            this.reload();
        });

        this.env.bus.addEventListener('reload_dashboard', () => {
            this.reload();
        });
    }

    async reload(domain = []) {
        if (this.isDestroyed) {
            console.warn("⚠️ Skip reload karena komponen sudah dihancurkan");
            return;
        }

        const savedState = this.loadState();

        const combinedDomain = domain.length
            ? domain
            : this.props.domain
                ? [...this.props.domain, ...(savedState.domain || [])]
                : (savedState.domain || []);

        this.state.domain = combinedDomain || [];
        console.log("🔥 Reload NumberCard dengan domain:", combinedDomain);

        try {
            await this.getStatistics(combinedDomain);
        } catch (err) {
            if (!this.isDestroyed) {
                console.error("❌ Error saat reload NumberCard:", err);
            }
        }
    }



    async getStatistics(domain = []) {
        const field = this.props.field || "count";
        const result = await this.orm.call(
            this.props.model,
            "get_statistics",
            [domain, field]
        );
        this.state.val = result;
    }

    openRecord() {
        const domain = this.state.domain;
        const context = this.props.context || {};
        // console.log("openRecord NumberCard with domain, conntext:", domain, context);
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            name: this.props.title,
            res_model: this.props.model,
            domain: domain ,
            context: context,
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
        });
    }

    loadState() {
        try {
            const savedState = localStorage.getItem('kermaDashboardState');
            if (!savedState) return {};
            
            const parsedState = JSON.parse(savedState);
            // Ensure domain arrays are properly restored
            return {
                ...parsedState,
                unitDomain: parsedState.unitDomain || [],
                locationDomain: parsedState.locationDomain || [],
                keywordDomain: parsedState.keywordDomain || [],
                domain: parsedState.domain || []
            };
        } catch (error) {
            console.error('Error loading state:', error);
            return {};
        }
    }
}

