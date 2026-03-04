# SimplifiedScript 🚀

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange)](https://github.com/Infinite-Networker/SimiplifiedScript/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**SimplifiedScript** is a powerful, user-friendly programming language specifically designed for AI programs to connect to networking systems and legally access data from online open-source databases. It features an intuitive syntax that makes it accessible even to those with minimal programming experience.

---

## 🌟 Key Features

- **🤖 AI-Focused Design** – Purpose-built for AI data acquisition and storage
- **🔌 Seamless API Integration** – Built-in `fetch()` with automatic JSON parsing
- **📁 File I/O Operations** – `read()` and `write()` data with simple commands
- **🛡️ Robust Error Handling** – `try / catch` blocks and comprehensive debugging
- **📊 Rich Data Types** – Integers, floats, strings, booleans, arrays, and dictionaries
- **🎯 Intuitive Syntax** – Plain English commands for easy learning
- **⚡ Fast Execution** – Lightweight interpreter written in Python 3

---

## 📦 Installation

### Option 1 – From Source (recommended)

```bash
git clone https://github.com/Infinite-Networker/SimiplifiedScript.git
cd SimiplifiedScript
# No external dependencies required – pure Python 3 standard library only
python interpreter.py --help
```

### Option 2 – Quick Start (no install)

```bash
python interpreter.py my_program.ss
```

---

## 🚀 Usage

### Run a script

```bash
python interpreter.py your_first_program.ss
```

Or use the provided helper shell script:

```bash
chmod +x run_script.sh
./run_script.sh your_first_program.ss
```

### Interactive REPL

Launch the REPL by running the interpreter with no arguments:

```bash
python interpreter.py
```

Example session:

```
SimplifiedScript REPL v1.0.0
Type 'exit()' or press Ctrl+C to quit.

>>> let name = "SimplifiedScript";
>>> print("Hello, " + name);
Hello, SimplifiedScript
>>> exit()
Goodbye!
```

---

## 📖 Language Reference

### Comments

```ss
# This is a comment
```

### Variables

```ss
let name = "Developer";
let count = 42;
let pi = 3.14;
let active = true;
```

### Print

```ss
print("Hello, " + name + "!");
```

### Arithmetic & String Concatenation

```ss
let sum = 10 + 5;
let msg = "Result: " + sum;
```

### Conditionals

```ss
if (count > 10) {
    print("Greater than 10");
} else if (count == 10) {
    print("Exactly 10");
} else {
    print("Less than 10");
}
```

### While Loops

```ss
let i = 0;
while (i < 5) {
    print("i = " + i);
    i = i + 1;
}
```

### Functions

```ss
func greet(name) {
    return "Hello, " + name + "!";
}
print(greet("World"));
```

### Arrays

```ss
let colors = ["red", "green", "blue"];
print(colors[0]);   # red
```

### Dictionaries

```ss
let person = {"name": "Alice", "age": 30};
print(person["name"]);   # Alice
```

### Fetch Data from an API

```ss
try {
    let data = fetch("https://api.example.com/data");
    print("Response: " + data["key"]);
} catch (error) {
    print("Failed to fetch: " + error);
}
```

### File I/O

```ss
# Write
write("output.json", {"key": "value"});

# Read
let content = read("output.json");
print(content);
```

### Error Handling

```ss
try {
    let result = fetch("https://api.example.com/data");
    print(result["value"]);
} catch (err) {
    print("Error: " + err);
}
```

---

## 📂 Example Files

| File | Description |
|------|-------------|
| `hello_world.ss` | Your very first SimplifiedScript program |
| `your_first_program.ss` | Variables, comments, and string concatenation |
| `fetch_data_from_api.ss` | Live API call with `fetch()` and error handling |
| `file_operations.ss` | `write()` and `read()` with a JSON dictionary |
| `interactive_repl_demo.ss` | Demonstrates REPL-style interaction |
| `install_from_source.sh` | Shell script to clone and set up the project |
| `run_script.sh` | Shell script helper to run any `.ss` file |
| `interpreter.py` | The SimplifiedScript interpreter (entry point) |

---

## 🛠️ Supported Operators

| Category | Operators |
|----------|-----------|
| Arithmetic | `+`  `-`  `*`  `/`  `%` |
| Comparison | `==`  `!=`  `<`  `>`  `<=`  `>=` |
| Logical | `&&`  `\|\|`  `!` |
| Assignment | `=` |
| String concat | `+` (auto-converts numbers to strings) |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
