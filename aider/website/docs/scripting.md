---
parent: More info
nav_order: 400
description: You can script aider via the command line or python.
---

# Scripting aider

You can script aider via the command line or python.

## Command line

Aider takes a `--message` argument, where you can give it a natural language instruction.
It will do that one thing, apply the edits to the files and then exit.
So you could do:

```bash
aider --message "make a script that prints hello" hello.js
```

Or you can write simple shell scripts to apply the same instruction to many files:

```bash
for FILE in *.py ; do
    aider --message "add descriptive docstrings to all the functions" $FILE
done
```

Use `aider --help` to see all the 
[command line options](/docs/config/options.html),
but these are useful for scripting:

```
--stream, --no-stream
                      Enable/disable streaming responses (default: True) [env var:
                      AIDER_STREAM]
--message COMMAND, --msg COMMAND, -m COMMAND
                      Specify a single message to send GPT, process reply then exit
                      (disables chat mode) [env var: AIDER_MESSAGE]
--message-file MESSAGE_FILE, -f MESSAGE_FILE
                      Specify a file containing the message to send GPT, process reply,
                      then exit (disables chat mode) [env var: AIDER_MESSAGE_FILE]
--yes                 Always say yes to every confirmation [env var: AIDER_YES]
--auto-commits, --no-auto-commits
                      Enable/disable auto commit of GPT changes (default: True) [env var:
                      AIDER_AUTO_COMMITS]
--dirty-commits, --no-dirty-commits
                      Enable/disable commits when repo is found dirty (default: True) [env
                      var: AIDER_DIRTY_COMMITS]
--dry-run, --no-dry-run
                      Perform a dry run without modifying files (default: False) [env var:
                      AIDER_DRY_RUN]
--commit              Commit all pending changes with a suitable commit message, then exit
                      [env var: AIDER_COMMIT]
--auto-test, --no-auto-test
                      Enable/disable automatic testing after changes (default: False) [env var:
                      AIDER_AUTO_TEST]
--test-cmd TEST_CMD   Specify command to run tests [env var: AIDER_TEST_CMD]
```

### Verifying headless changes with tests

By default, a scripted `--message` run applies aider's edits and exits,
without checking that the result still compiles or passes tests.
Combine `--auto-test` with `--test-cmd` to have aider run your test
suite after each round of edits and automatically attempt to fix any
failures, just like it does in an interactive session:

```bash
aider --message "fix the failing tests in the payments module" \
    --yes-always \
    --no-auto-commits \
    --auto-test \
    --test-cmd "go build ./... && go test ./..."
```

The test command should print errors on stdout/stderr
and return a non-zero exit code when the tests fail.
Aider will feed that output back to the model and retry,
for up to three reflection rounds.
This makes `--message` runs much safer for CI jobs and benchmarks,
where nobody is watching to catch broken output.

See
[linting and testing](/docs/usage/lint-test.html)
for more about configuring test commands,
including per-language lint commands.


## Python

You can also script aider from python:

```python
from aider.coders import Coder
from aider.models import Model

# This is a list of files to add to the chat
fnames = ["greeting.py"]

model = Model("gpt-4-turbo")

# Create a coder object
coder = Coder.create(main_model=model, fnames=fnames)

# This will execute one instruction on those files and then return
coder.run("make a script that prints hello world")

# Send another instruction
coder.run("make it say goodbye")

# You can run in-chat "/" commands too
coder.run("/tokens")

```

See the
[Coder.create() and Coder.__init__() methods](https://github.com/Aider-AI/aider/blob/main/aider/coders/base_coder.py)
for all the supported arguments.

It can also be helpful to set the equivalent of `--yes` by doing this:

```python
from aider.io import InputOutput
io = InputOutput(yes=True)
# ...
coder = Coder.create(model=model, fnames=fnames, io=io)
```

{: .note }
The python scripting API is not officially supported or documented,
and could change in future releases without providing backwards compatibility.
