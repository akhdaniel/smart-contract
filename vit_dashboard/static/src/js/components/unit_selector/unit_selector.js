/** @odoo-module **/

import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { useService } from "@web/core/utils/hooks";
import { fuzzyLookup } from "@web/core/utils/search";
import { _t } from "@web/core/l10n/translation";

import { Component, onWillStart, useState } from "@odoo/owl";

export class UnitSelector extends Component {
    setup() {
        this.orm = useService("orm");

        this.state = useState({
            value: this.props.value || "", // Initialize the input value
        });

        onWillStart(async () => {
            // if (!this.props.units) {
            //     this.units = await this._fetchAvailableUnits();
            // } else {
            //     this.units = await this.orm.call("operating.unit", "display_name_for", [
            //         this.props.units,
            //     ]);
            // }

            // this.units = this.units.map((record) => ({
            //     id: record.id, // Use the record's id from the server
            //     label: record.name, // Use the record's name as the label
            // }));

            // console.log("Available units:", this.units);

        });
    }

    get placeholder() {
        return _t("Search Unit Kerja...");
    }

    get sources() {
        // console.log("optionsSource", this.optionsSource);
        return [this.optionsSource];
    }

    get optionsSource() {
        return {
            placeholder: _t("Loading..."),
            // options: this.loadOptionsSource.bind(this),
            options: (request) => this.loadOptionsSource(request),

        };
    }

    onSelect(option) {
        // console.log("Selected option:", option);
        const obj = Object.getPrototypeOf(option);
        // Update the input value with the selected unit's label
        this.state.value = obj.label;

        // Notify the parent component about the selected unit
        this.props.onUnitSelected({
            id: obj.id,
            name: obj.label,
        });
    }

    onInput(event) {
        const inputValue = event.target.value;
        this.state.value = inputValue; // Update the input value as the user types

        if (!inputValue.trim()) {
            console.log("Reset selection values when input is empty", inputValue);
            if (this.props.onUnitSelected) {
                this.props.onUnitSelected(null); // Notify parent to reset the selection
            }
        }
    }

    filterUnits(name) {
        if (!name) {
            return this.units;
        }
        return fuzzyLookup(name, this.units, (unit) => unit.label);
    }

    loadOptionsSource(request) {
        const options = this.filterUnits(request);
        // console.log("Filtered options:", options, request);

        if (!options.length) {
            options.push({
                label: _t("No records"),
                classList: "o_m2o_no_result",
                unselectable: true,
            });
        }
        return options;
        
    }

    // async _fetchAvailableUnits() {
    //     const result = await this.orm.searchRead(
    //         "operating.unit",
    //         [["is_ada_kerjasama", "=", true]],
    //         ["id", "name"]
    //     );
    //     return result || [];
    // }
}

UnitSelector.template = "web.UnitSelector";
UnitSelector.components = { AutoComplete };
UnitSelector.props = {
    onUnitSelected: Function,
    id: { type: String, optional: true },
    value: { type: String, optional: true },
    units: { type: Array, optional: true },
};
