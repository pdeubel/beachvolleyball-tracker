// Use a map to map from player id to the player's name, and add the initial player
let player_name_map = new Map();
player_name_map.set(current_player_id, current_player_name);
let scanned_players = [current_player_id];

let player_team_map = new Map();

const add_data_div = document.getElementById("add-data-here");


function onScanSuccess(decodedText, decodedResult) {
    let data = new FormData();
    data.append("scanned_data", decodedText);

    fetch('/game/player-lookup', {
        "method": "POST",
        "body": data
    }).then(response => {
        return response.json();
    }).then(json_response => {
        let player_name = json_response["player_name"];

        let player_id = json_response["player_id"];
        let pos = scanned_players.indexOf(player_id);

        // If pos is -1 then the scanned player is a new player, so add it to the list
        if (pos < 0) {
            let player_span = document.createElement('span');
            player_span.classList.add('badge', 'bg-primary', 'me-2', 'player-badge');
            let player_name_text = document.createTextNode(player_name);
            player_span.appendChild(player_name_text);
            add_data_div.appendChild(player_span);

            scanned_players.push(player_id);
            player_name_map.set(player_id, player_name);
        }
    }).catch(err => {
        console.log("Error:", err)
    });
}


function selectTeamsCallback() {
    let data = {
        "players": scanned_players
    };

    fetch('/game/select-teams', {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(data)
    }).then(response => {
        // window.location.href = response.redirect;
        return response.json();
    }).then(responseJSON => {
        // Remove select teams button as it is no longer needed

        const btn = document.getElementById("btn-select-teams");
        btn.remove();

        let team_1_ids = responseJSON["team_1"]
        let team_2_ids = responseJSON["team_2"]  // May be empty!

        // Clear add_data div and add the two teams
        add_data_div.innerHTML = "";

        function changeClassOnClick() {
            let player_id = parseInt(this.getAttribute("player_id"));
            let current_team = player_team_map.get(player_id);

            if (current_team === 0) {
                this.classList.replace("bg-success", "bg-danger");
                player_team_map.set(player_id, 1);
            } else {
                this.classList.replace("bg-danger", "bg-success");
                player_team_map.set(player_id, 0);
            }
        }

        function createTeamSpanForPlayer(team, player_id) {
            player_team_map.set(player_id, team);

            let badgeType = "bg-success";

            if (team === 1) {
                badgeType = "bg-danger";
            }

            let player_span = document.createElement('span');
            player_span.classList.add('badge', badgeType, 'me-2', 'player-badge');
            player_span.setAttribute("player_id", player_id);
            let player_name_text = document.createTextNode(player_name_map.get(player_id));
            player_span.appendChild(player_name_text);
            player_span.addEventListener("click", changeClassOnClick);
            add_data_div.appendChild(player_span);
        }

        team_1_ids.forEach(player_id => {
            createTeamSpanForPlayer(0, player_id);
        });

        team_2_ids.forEach(player_id => {
            createTeamSpanForPlayer(1, player_id);
        });

        const btn_div = document.getElementById("button-div");
        let start_game_btn = document.createElement("button")
        start_game_btn.setAttribute("type", "button");
        start_game_btn.classList.add("btn", "btn-primary");
        start_game_btn.setAttribute("data-bs-toggle", "modal");
        start_game_btn.setAttribute("data-bs-target", "#confirmTeamModal");

        let start_game_btn_text = document.createTextNode("Spiel starten");
        start_game_btn.appendChild(start_game_btn_text);
        btn_div.appendChild(start_game_btn);
    }).catch(err => {
        console.log(err);
    });
}


function confirmTest () {
    fetch("/game/create-game", {
        "method": "POST",
        "headers": {'Content-Type': 'application/json'},
        "body": JSON.stringify(Object.fromEntries(player_team_map))  // JSON.stringify nulls js Map, so use fromEntries
    }).then(res => {
        window.location.href = res.url;
    });
}

// Insert QR Code Reader
let html5QrcodeScanner = new Html5QrcodeScanner("qr-reader", { fps: 10, qrbox: {width: 250, height: 250} });
html5QrcodeScanner.render(onScanSuccess);

// Register the callback for the select teams button
let select_teams_button = document.getElementById("btn-select-teams");
select_teams_button.addEventListener("click", selectTeamsCallback);

let confirm_teams_button = document.getElementById("btn-confirm-teams");
confirm_teams_button.addEventListener("click", confirmTest);