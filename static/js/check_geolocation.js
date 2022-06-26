/* Source: https://stackoverflow.com/a/13841047 (Frank van Puffelen) */
function distance(lat1, lon1, target_lat, target_lon) {
    const R = 6371; // Radius of the earth in km
    const dLat = (target_lat - lat1).toRad();  // Javascript functions in radians
    const dLon = (target_lon - lon1).toRad();
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1.toRad()) * Math.cos(target_lat.toRad()) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const d = R * c; // Distance in km
    return d * 1000;  // Distance in m
}

/** Converts numeric degrees to radians */
if (typeof (Number.prototype.toRad) === "undefined") {
    Number.prototype.toRad = function () {
        return this * Math.PI / 180;
    }
}

let location_in_radius = true;

window.navigator.geolocation.getCurrentPosition(pos => {
    let dist = distance(pos.coords.latitude, pos.coords.longitude, beach_location_latitude, beach_location_longitude);
    location_in_radius = dist <= allowed_distance_in_meter;

    let data = new FormData();
    data.set("location_in_radius", location_in_radius);

    fetch("/game", {
        "method": "POST",
        "body": data
    }).then(res => {
        window.location = res.url;
    });
});
