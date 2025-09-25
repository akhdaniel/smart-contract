/** @odoo-module **/

import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { useService } from "@web/core/utils/hooks";
import { fuzzyLookup } from "@web/core/utils/search";
import { _t } from "@web/core/l10n/translation";

import { Component, onWillStart } from "@odoo/owl";

export class MitraSelector extends Component {
    setup() {
        this.orm = useService("orm");

        onWillStart(async () => {
            if (!this.props.mitras) {
                this.mitras = await this._fetchAvailableMitras();
            } else {
                this.mitras = await this.orm.call("res.partner", "display_name_for", [
                    this.props.mitras,
                ]);
            }

            this.mitras = this.mitras.map((record) => ({
                id: record.id,
                label: record.name,
                classList: {
                    [`o_model_selector_${record.name}`]: 1,
                },
            }));
        });
    }

    get placeholder() {
        return _t("Search a Mitra...");
    }

    get sources() {
        return [this.optionsSource];
    }
    get optionsSource() {
        return {
            placeholder: _t("Loading..."),
            options: this.loadOptionsSource.bind(this),
        };
    }

    onSelect(option) {
        this.props.onMitraSelected({
            id: option.id,
            name: option.label,
        });
    }

    filterMitras(name) {
        if (!name) {
            return this.mitras;
        }
        return fuzzyLookup(name, this.mitras, (unit) => unit.label );
    }

    loadOptionsSource(request) {
        const options = this.filterMitras(request);

        if (!options.length) {
            options.push({
                label: _t("No records"),
                classList: "o_m2o_no_result",
                unselectable: true,
            });
        }
        return options;
    }

    /**
     * Fetch the list of the models that can be
     * selected for the relational properties.
     */
    async _fetchAvailableMitras() {
        const result = await this.orm.searchRead("res.partner", [['is_mitra','=',true]], ["id","name"]);
        return result || [];
    }
}

MitraSelector.template = "web.MitraSelector";
MitraSelector.components = { AutoComplete };
MitraSelector.props = {
    onMitraSelected: Function,
    id: { type: String, optional: true },
    value: { type: String, optional: true },
    // list of models name name, if not set
    // we will fetch all models we have access to
    mitras: { type: Array, optional: true },
};
