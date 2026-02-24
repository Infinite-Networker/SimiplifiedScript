# Save data to file
let data = {
    "name": "SimplifiedScript",
    "version": 1.0,
    "features": ["API", "File I/O", "Error Handling"]
};
write("data.json", data);

# Read it back
let saved = read("data.json");
print("Saved data: " + saved);
