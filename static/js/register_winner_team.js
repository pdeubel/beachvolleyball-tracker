select_winner_team_alert_div = document.getElementById("select-winner-team-alert-id");
let winner_team = null;

let winner_team_btn_group = document.getElementById("winner-team-btn-group");
winner_team_btn_group.addEventListener("click", () => {
    if (select_winner_team_alert_div.classList.contains("collapse.show")) {
        // Alert for selecting team has been shown, remove it as one team was at least selected
        select_winner_team_alert_div.remove();
    }

    set_game_winner_btn.setAttribute("data-bs-toggle", "modal");
    set_game_winner_btn.setAttribute("data-bs-target", "#confirmWinnerTeamModal");
});


let winner_team_first = document.getElementById("winner-team-first");
let winner_team_second = document.getElementById("winner-team-second");

let winner_team_confirm_label = document.getElementById("winner-team-confirm-label-id");
let confirmation_div_first_team = document.getElementById("winner-team-confirm-list-first-team-id");
let confirmation_div_second_team = document.getElementById("winner-team-confirm-list-second-team-id");

winner_team_first.addEventListener("click", () => {
    // This and the code in the winner_team_second event listener ensures that the button stays "active" (colored),
    // even when clicking somewhere else, for example on another button not part of the btn group
    winner_team_second.classList.remove("active");
    winner_team_first.classList.add("active");

    winner_team = 0;

    winner_team_confirm_label.innerText = "Team 1";

    confirmation_div_first_team.classList.remove("collapse");
    confirmation_div_first_team.classList.add("collapse.show");

    confirmation_div_second_team.classList.remove("collapse.show");
    confirmation_div_second_team.classList.add("collapse");
});

winner_team_second.addEventListener("click", () => {
    winner_team_first.classList.remove("active");
    winner_team_second.classList.add("active");

    winner_team = 1;

    winner_team_confirm_label.innerText = "Team 2";

    confirmation_div_second_team.classList.remove("collapse");
    confirmation_div_second_team.classList.add("collapse.show");

    confirmation_div_first_team.classList.remove("collapse.show");
    confirmation_div_first_team.classList.add("collapse");
});

set_game_winner_btn = document.getElementById("set-game-winner-btn");
set_game_winner_btn.addEventListener("click", (event) => {
    if (winner_team == null) {
        select_winner_team_alert_div.classList.remove("collapse");
        select_winner_team_alert_div.classList.add("collapse.show");
    }
});


confirm_winner_btn = document.getElementById("confirm-winner-team-btn");
confirm_winner_btn.addEventListener("click", () => {
    let data = new FormData();
    data.set("winner_team", winner_team);
    data.set("game_id", game_id);

    fetch("/game/register-winner", {
        "method": "POST",
        "body": data
    }).then(() => {
        let winner_content_div = document.getElementById("select-winner-content-div");
        winner_content_div.classList.add("collapse");

        let confirm_submitted_winner_label = document.getElementById("confirm-submitted-winner-label");

        // winner_team is 0 if its Team 1 or 1 if its Team 2, therefore simply add 1
        confirm_submitted_winner_label.innerText = (winner_team + 1).toString();

        let confirm_submitted_winner_div = document.getElementById("confirm-submitted-winner-div");
        confirm_submitted_winner_div.classList.replace("collapse", "collapse.show");
    }).catch(err => {
        console.log("Error: ", err);
    })
})