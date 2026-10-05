/** @odoo-module **/

import { ActivityMenu } from "@mail/core/web/activity_menu";
import { patch } from "@web/core/utils/patch";

const originalSetup = ActivityMenu.prototype.setup;
const originalOpenActivityGroup = ActivityMenu.prototype.openActivityGroup;

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

patch(ActivityMenu.prototype, {
    setup() {
        originalSetup.call(this);
        this.activityBusService = this.env.services.bus_service;
        this.activityBusService.subscribe("vit.activity_menu/updated", () => {
            this.fetchSystrayActivities();
        });
    },

    openActivityGroup(group, filter) {
        if (group.model === "vit.syarat_termin") {
            return this.openPaymentDocumentsPending(group);
        }
        return originalOpenActivityGroup.call(this, group, filter);
    },

    openIzinPrinsipSoon(group) {
        document.body.click();
        const today = new Date();
        const reminderLimit = new Date(today);
        reminderLimit.setDate(reminderLimit.getDate() + 7);
        this.action.doAction({
            type: "ir.actions.act_window",
            name: group.name,
            res_model: "vit.izin_prinsip",
            views: this.availableViews(group),
            view_type: group.view_type,
            domain: [
                ["active", "=", true],
                ["stage_is_done", "=", true],
                ["batas_waktu_izin_prinsip", ">=", formatDate(today)],
                ["batas_waktu_izin_prinsip", "<=", formatDate(reminderLimit)],
                ["kontrak_ids", "=", false],
            ],
            context: { force_search_count: 1 },
        }, {
            clearBreadcrumbs: true,
            viewType: group.view_type,
        });
    },

    openPaymentDocumentsPending(group) {
        document.body.click();
        this.action.doAction({
            type: "ir.actions.act_window",
            name: group.name,
            res_model: "vit.syarat_termin",
            views: this.availableViews(group),
            view_type: group.view_type,
            domain: [
                ["document", "!=", false],
                [group.verification_pending_field || "verified", "=", false],
            ],
            context: { force_search_count: 1 },
        }, {
            clearBreadcrumbs: true,
            viewType: group.view_type,
        });
    },
});
