/** @odoo-module **/

import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets"; //
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, useState, onMounted, useRef } = owl;
import { NumberCardSarlog } from "../number_card/number_card_sarlog";

export class SarlogDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.CanvasRef = useRef("canvas");

        this.state = useState({
            masterBudgets: [],
            totalSummary: {},
            kanwilDroping: [],
            kanwilRealisasi: [],
        });

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");

            const result = await this.orm.call(
                "vit.budget_rkap",
                "get_statistics_sarlog",
                []
            );
            this.state.masterBudgets = result.master_list || [];
            this.state.totalSummary = result.total_summary || {};

            // ambil data droping per kanwil
            try {
                const dropingData = await this.orm.call(
                    "vit.budget_rkap",
                    "get_droping_by_kanwil",
                    []
                );
                this.state.kanwilDroping = dropingData || [];
            } catch (e) {
                console.warn("Failed to fetch droping data:", e);
                this.state.kanwilDroping = [];
            }


            try {
                const realisasiData = await this.orm.call(
                    "vit.budget_rkap",
                    "get_realisasi_by_kanwil",
                    []
                );
                this.state.kanwilRealisasi = realisasiData || [];
            } catch (e) {
                console.warn("Failed to fetch realisasi data:", e);
                this.state.kanwilRealisasi = [];
            }
        });

        // render chart setelah component mounted
        onMounted(() => {
            setTimeout(() => this.renderChart(), 400);
        });
    }

    async getstatistics() {
        try {
            const result = await this.orm.call(
                this.props.model,
                "get_statistics_sarlog",
                []
            );

            this.state.masterBudgets = result.master_list || [];
            this.state.totalSummary = result.total_summary || {};
        } catch (error) {
            console.error("❌ Error loading SarlogDashboard:", error);
            this.state.masterBudgets = [];
            this.state.totalSummary = {};
        }
    }

    renderChart() {
        if (!this.state.kanwilDroping.length) return;
        const el = document.getElementById("dropingChart");
        if (!el) return;
        const ctx = el.getContext("2d");

        const labels = this.state.kanwilDroping.map(d => d.kanwil_name);
        const data = this.state.kanwilDroping.map(d => d.persen_droping);

        if (window.Chart) {
            new window.Chart(ctx, {
                type: "bar",
                data: {
                    labels,
                    datasets: [{
                        label: "Persentase Droping (%)",
                        data,
                        backgroundColor: "#007bff",
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            ticks: {
                                autoSkip: false,
                                maxRotation: 45,
                                minRotation: 45,
                                font: { size: 10 },
                            },
                        },
                        y: {
                            beginAtZero: true,
                            max: 100,
                        },
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: "top",
                            align: "center",
                        },
                    },
                },
            });
        }
    }



    onYearChange(ev) {
        const selectedYear = parseInt(ev.target.value);
        this.state.selectedYear = selectedYear;
        console.log("📅 Tahun dipilih:", selectedYear);
    }

}

SarlogDashboard.template = "vit_dashboard.SarlogDashboard";
SarlogDashboard.components = { NumberCardSarlog };

registry.category("actions").add("vit_dashboard.SarlogDashboard", SarlogDashboard);
