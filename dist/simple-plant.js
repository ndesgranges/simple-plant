
const CARD_TYPE="simple-plant-card";
const CARD_NAME="Simple Plant Card";
const CARD_DESCRIPTION="Custom card for simple-plant integration";

const CARD_VERSION="v0.0.7";
const CARD_AUTHOR="ndesgranges";

console.info(
    `%c 🪴 ${CARD_NAME} 🪴 %c ${CARD_VERSION} \n%c  By @${CARD_AUTHOR}`,
    "color: green; background: white; font-weight: bold; border: solid 1px green; border-radius: 4px 0 0 4px",
    "color: white; background: green; font-weight: bold; border: solid 1px green; border-radius:  0 4px 4px 0",
    "color: green;",
);

class SimplePlantCard extends HTMLElement {

    // properties
    config;
    hass;
    elements = {};

    constructor() {
        super();
        this.renderCard();
        this.createStyles()
        // Create shadow root
        this.attachShadow({ mode: "open" });
        this.shadowRoot.append(this.elements.style, this.elements.card);
    }

    // Updating content
    set hass(hass) {

        this.hass = hass
        this.updateCard()
    }

    setConfig(config) {
        if (!config.entity) {
            throw new Error("You need to define an entity");
        }
        this.config = config;
    }

    // Create card and its content
    renderCard() {
        // root
        this.elements.card = document.createElement("ha-card");
        // card content (wrapper)
        this.elements.cardContent = document.createElement("div")
        this.elements.cardContent.classList.add("card-content");
        this.elements.cardContent.innerHTML = `
            <div>TEST CONTENT</div>
            `;


        // add card content to the card
        this.elements.card.append(this.elements.cardContent)
    }

    // Get style element
    createStyles() {
        this.elements.style = document.createElement("style");
        this.elements.style.textContent = `
            .error {
                color: red;
            }
            `;
    }

    // Hass Updated
    updateCard() {

    }

    getCardSize() {
        return 1;
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

customElements.define(CARD_TYPE, SimplePlantCard);

// Register for the visual selection in the UI
window.customCards = window.customCards || [];
window.customCards.push({
    type: CARD_TYPE,
    name: CARD_NAME,
    description: CARD_DESCRIPTION
});