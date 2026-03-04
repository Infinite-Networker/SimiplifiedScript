# Fetch weather data from a public API with error handling
try {
    let weather = fetch("https://api.weather.gov/points/39.7456,-97.0892");
    let forecast = fetch(weather["properties"]["forecast"]);
    let period = forecast["properties"]["periods"][0];
    print("Current conditions: " + period["shortForecast"]);
    print("Temperature: " + period["temperature"] + "°" + period["temperatureUnit"]);
} catch (error) {
    print("Error fetching weather data: " + error);
}
