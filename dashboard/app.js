const WS_URL = "wss://phoenix-brain.onrender.com/ws";

let socket;
const connectionPulse = document.getElementById("connection-pulse");
const connectionStatus = document.getElementById("connection-status");
const offerFeed = document.getElementById("offer-feed");
const emptyState = document.getElementById("empty-state");

function connect() {
    socket = new WebSocket(WS_URL);

    socket.onopen = function (e) {
        console.log("[open] Connection established");
        connectionPulse.classList.remove("disconnected");
        connectionPulse.classList.add("connected");
        connectionStatus.textContent = "Uplink Active";
    };

    socket.onmessage = function (event) {
        try {
            const payload = JSON.parse(event.data);
            if (payload.type === "new_offer") {
                handleNewOffer(payload.offer, payload.evaluation);
            }
        } catch (error) {
            console.error("Error parsing WebSocket message:", error);
        }
    };

    socket.onclose = function (event) {
        connectionPulse.classList.add("disconnected");
        connectionPulse.classList.remove("connected");
        connectionStatus.textContent = "Disconnected - Retrying...";
        setTimeout(connect, 3000);
    };

    socket.onerror = function (error) {
        console.error(`[error] WebSocket error observed`);
    };
}

function handleNewOffer(offer, evaluation) {
    if (emptyState) {
        emptyState.style.display = "none";
    }

    const card = document.createElement("div");

    // Determine AI recommendation classes
    let cardClassCode = "card-ignore";
    let decisionCode = "ignore";

    if (evaluation.decision === "ACCEPT") {
        cardClassCode = "card-accept";
        decisionCode = "accept";
    } else if (evaluation.decision === "DECLINE") {
        cardClassCode = "card-decline";
        decisionCode = "decline";
    }

    card.className = `glass-panel offer-card ${cardClassCode}`;
    const platformClass = offer.platform.toLowerCase() === 'lyft' ? 'lyft' : 'uber';

    // Add glowing color logic to the dollar-per-mile value
    const dpmColor = evaluation.dollars_per_mile >= 1.0 ? 'var(--secondary)' : 'var(--danger)';

    card.innerHTML = `
        <div class="card-header">
            <div class="platform-badge ${platformClass}">
                ${offer.platform.toUpperCase()}
            </div>
            <div class="fare-block">
                <div class="fare-amount">$${offer.fare.toFixed(2)}</div>
                <div class="fare-label">Upfront Fare</div>
            </div>
        </div>

        <div class="card-body">
            <div class="ai-score-block">
                <div class="score-circle ${getScoreClass(evaluation.score)}">
                    ${evaluation.score}
                </div>
                <div class="ai-recommendation">
                    <span class="title">AI Engine Decision</span>
                    <span class="decision ${decisionCode}">${evaluation.decision}</span>
                </div>
            </div>

            <div class="metric-box">
                <div class="metric-label">Value Metric</div>
                <div class="metric-val" style="color: ${dpmColor}">$${evaluation.dollars_per_mile.toFixed(2)}</div>
                <div class="metric-sub">Per Mile Average</div>
            </div>

            <div class="metric-box">
                <div class="metric-label">Hourly Est</div>
                <div class="metric-val">$${(evaluation.dollars_per_hour || 0).toFixed(2)}</div>
                <div class="metric-sub">Projected Earnings</div>
            </div>

            <div class="metric-box">
                <div class="metric-label">Total Distance</div>
                <div class="metric-val">${offer.total_miles} <span style="font-size:1rem; color:var(--text-muted)">mi</span></div>
                <div class="metric-sub">Pickup: ${offer.pickup_miles} mi &bull; Trip: ${offer.trip_miles} mi</div>
            </div>

            <div class="metric-box">
                <div class="metric-label">Total Time</div>
                <div class="metric-val">${offer.total_minutes} <span style="font-size:1rem; color:var(--text-muted)">min</span></div>
                <div class="metric-sub">Pickup Time: ${offer.pickup_minutes} min</div>
            </div>
        </div>

        <div class="card-raw-toggle" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block'">
            [ View Raw Matrix Payload ]
        </div>
        <div class="raw-data-box">
            ${offer.raw_text}
        </div>
    `;

    // Drop it directly into the top of the feed grid
    offerFeed.insertBefore(card, offerFeed.firstChild);

    // Keep the feed clean: only hold the last 15 mega-cards
    if (offerFeed.children.length > 15 && offerFeed.lastChild.id !== 'empty-state') {
        offerFeed.removeChild(offerFeed.lastChild);
    }
}

function getScoreClass(score) {
    if (score >= 70) return "score-high";
    if (score >= 40) return "score-mid";
    return "score-low";
}

// Boot stream
connect();
