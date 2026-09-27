# Python Automation Portfolio

Small, complete Python tools built end-to-end: specification, implementation, tests, documentation.

Each project uses **only the Python standard library** — no external dependencies.

---

## Projects

### wordcount

Word frequency counter for text files. Shows the top-N most frequent words.

- CLI options: `--top N`, `--min-length N`
- Tests: 20 (unittest)
- Stack: Python 3.8+, stdlib only

### csv2json

CSV to JSON converter with header detection, malformed row handling, and processing report.

- Features: header/no-header modes, skip and report invalid rows, indented output
- Tests: 7 (unittest)
- Stack: Python 3.8+, stdlib only

### todo-cli

Command-line todo manager with JSON file persistence.

- Commands: add, list, done, rm
- Features: auto-incremental IDs, persistent storage
- Tests: 43 (unittest)
- Stack: Python 3.8+, stdlib only

---

## How to run any project

    cd <project>
    python3 -m unittest -v
    python3 <project>.py --help

---

## About

I build autonomous AI systems and automation tools. These projects were produced
end-to-end (specification, code, tests, documentation) using a custom multi-agent
AI framework I designed from scratch.

Freelance: AI agents & workflow automation
