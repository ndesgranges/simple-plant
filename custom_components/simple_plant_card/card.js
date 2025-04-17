class SimplePlantCard extends HTMLElement {

    // Updating content
    set hass(hass) {

        const entityId = this.config.entity;
        const state = hass.states[entityId];
        const stateStr = state ? state.state : "unavailable";

        // Initialize the content if it's not there yet.
        if (!this.content) {
            // user makes sense here as every login gets it's own instance
            this.innerHTML = `
                <ha-card header="Hello ${hass.user.name}!">
                    <div class="card-content"></div>
                </ha-card>
            `;
            this.content = this.querySelector('div');
        }

        this.content.innerHTML = `
            <p>The ${entityId} is ${stateStr}.</p>
        `;
    }

    setConfig(config) {
        if (!config.entity) {
        throw new Error("You need to define an entity");
        }
        this.config = config;
    }

    getCardSize() {
        return 3;
    }

    // The rules for sizing your card in the grid in sections view
    getGridOptions() {
        return {
            rows: 3,
            columns: 6,
            min_rows: 3,
            max_rows: 3,
        };
    }
}

customElements.define('simple-plant-card', SimplePlantCard);