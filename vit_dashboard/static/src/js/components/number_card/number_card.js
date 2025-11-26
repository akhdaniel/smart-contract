/** @odoo-module */
const { Component, onMounted, onWillDestroy, useState } = owl;
import { useService } from "@web/core/utils/hooks";

export class NumberCard extends Component {
    static template = "vit_dashboard.NumberCard";
    static props = {
        title: { type: String },
        bgColor: { type: String, optional: true },
        textColor: { type: String, optional: true },
        icon: { type: String, optional: true },
        field: { type: String, optional: true },
        model: { type: String, optional: true },
        context: { type: Object, optional: true },
        domain: { type: Object, optional: true },
        onReload: { type: Function, optional: true },
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

    // async getStatistics(domain = []) {
    //     const field = this.props.field || "count";
    //     let result = {};

    //     try {
    //         result = await this.orm.call(
    //             this.props.model,
    //             "get_statistics",
    //             [domain, field]
    //         );
    //         console.log("🧮 RESULT DARI BACKEND:", field, result);
    //         this.state.val = { ...result };
    //     } catch (e) {
    //         console.error("❌ Error get_statistics:", field, e);
    //     }
    // }





    // openRecord() {
    //     const domain = this.state.domain;
    //     const context = this.props.context || {};
    //     // console.log("openRecord NumberCard with domain, conntext:", domain, context);
    //     this.env.services.action.doAction({
    //         type: 'ir.actions.act_window',
    //         name: this.props.title,
    //         res_model: this.props.model,
    //         domain: domain ,
    //         context: context,
    //         views: [[false, 'list'], [false, 'form']],
    //         target: 'current',
    //     });
    // }

    // openRecord() {
    //     const domain = this.state.domain;
    //     const context = this.props.context || {};
    //     const field = this.props.field;

    //     // 🔹 Kalau kartu yang diklik adalah "Total Qty Termin"
    //     if (field === 'total_qty_termin') {
    //         this.env.services.action.doAction({
    //             type: 'ir.actions.act_window',
    //             name: 'Syarat Termin Belum Diverifikasi',
    //             res_model: 'vit.syarat_termin',
    //             views: [[false, 'list'], [false, 'form']],
    //             target: 'current',

    //             // 🔸 Filter: Verified = False DAN Document tidak null
    //             domain: [
    //                 ['verified', '=', false],
    //                 ['document', '!=', false],
    //             ],

    //             // 🔸 Group by Kontrak biar tampil kayak gambar pertama
    //             context: {
    //                 group_by: ['kontrak_id'],
    //             },
    //         });
    //         return;
    //     }

    //     // 🔸 Default behavior buat kartu lainnya
    //     this.env.services.action.doAction({
    //         type: 'ir.actions.act_window',
    //         name: this.props.title,
    //         res_model: this.props.model,
    //         domain: domain,
    //         context: context,
    //         views: [[false, 'list'], [false, 'form']],
    //         target: 'current',
    //     });
    // }


    openRecord() {
        const domain = this.state.domain;
        const context = this.props.context || {};
        const field = this.props.field;

        if (field === 'total_qty_termin') {
            // Ambil filter Kanwil dan Budget Date dari domain dashboard
            const kanwilFilter = domain.find(d => d[0] === 'kanwil_id');
            const budgetDateFilter = domain.find(d => d[0] === 'budget_date');

            const terminDomain = [
                ['verified', '=', false],
                ['document', '!=', false],
            ];

            if (kanwilFilter) {
                terminDomain.push(['kontrak_id.kanwil_id', '=', kanwilFilter[2]]);
            }
            if (budgetDateFilter) {
                const selectedYear = new Date(budgetDateFilter[2]).getFullYear();

                const startDate = `${selectedYear}-01-01`;
                const endDate = `${selectedYear}-12-31`;

                terminDomain.push(['kontrak_id.budget_rkap_id.budget_date', '>=', startDate]);
                terminDomain.push(['kontrak_id.budget_rkap_id.budget_date', '<=', endDate]);
            }


            console.log("🟣 DOMAIN FINAL OPEN RECORD:", terminDomain);

            this.env.services.action.doAction({
                type: 'ir.actions.act_window',
                name: 'Syarat Termin Belum Diverifikasi',
                res_model: 'vit.syarat_termin',
                views: [[false, 'list'], [false, 'form']],
                target: 'current',
                domain: terminDomain,
                context: { group_by: ['kontrak_id'] },
            });
            return;
        }


        if (field === 'total_qty_payment') {
            const kanwilFilter = domain.find(d => d[0] === 'kanwil_id');
            const budgetDateFilter = domain.find(d => d[0] === 'budget_date');

            const paymentDomain = [
                ['stage_is_draft', '=', true],
            ];

            // 🔹 Filter berdasarkan Kanwil dari kontrak
            if (kanwilFilter) {
                paymentDomain.push(['kontrak_id.kanwil_id', '=', kanwilFilter[2]]);
            }

            // 🔹 Filter berdasarkan tahun dari Budget RKAP
            if (budgetDateFilter) {
                const selectedYear = new Date(budgetDateFilter[2]).getFullYear();
                const startDate = `${selectedYear}-01-01`;
                const endDate = `${selectedYear}-12-31`;
                paymentDomain.push(['kontrak_id.budget_rkap_id.budget_date', '>=', startDate]);
                paymentDomain.push(['kontrak_id.budget_rkap_id.budget_date', '<=', endDate]);
            }

            console.log("💰 DOMAIN FINAL OPEN RECORD PAYMENT:", paymentDomain);

            this.env.services.action.doAction({
                type: 'ir.actions.act_window',
                name: 'Pengajuan Pembayaran (Draft)',
                res_model: 'vit.payment',
                views: [[false, 'list'], [false, 'form']],
                target: 'current',

                domain: paymentDomain,
                context: { group_by: ['kontrak_id'] },
            });
            return;
        }

        return;  
        
        // const sanitizedDomain = (domain || []).map(d => {
        //     try {
        //         if (d && d.length >= 1 && d[0] === 'kanwil_id') {
        //             const left = (this.props.model === 'vit.budget_rkap')
        //                 ? 'izin_prinsip_ids.kanwil_id'
        //                 : 'kontrak_id.kanwil_id';
        //             return [left, d[1], d[2]];
        //         }
        //     } catch (e) {
        //     }
        //     return d;
        // });

        // this.env.services.action.doAction({
        //     type: 'ir.actions.act_window',
        //     name: this.props.title,
        //     res_model: this.props.model,
        //     domain: sanitizedDomain,
        //     context: context,
        //     views: [[false, 'list'], [false, 'form']],
        //     target: 'current',
        // });
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

