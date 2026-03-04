# Save data to file
let data = {
    "name": "SimplifiedScript",
    "version": 1.0,
    "features": ["API", "File I/O", "Error Handling"]
};

try {
    write("data.json", data);
    print("Data written successfully.");

    # Read it back
    let saved = read("data.json");
    print("Saved data: " + saved);
} catch (error) {
    print("File operation failed: " + error);
}
