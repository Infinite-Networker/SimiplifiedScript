# Fetch weather data
let weather = fetch("https://api.weather.gov/data");
print("Current temperature: " + weather["temp"] + "°C");
