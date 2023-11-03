# Setting up your development environment

## Thonny

Go to [the Thonny website](https://thonny.org/) and download the version for your operating system. It's available for Windows, macOS (both Intel and Apple Silicon), and for various versions of Linux.

After installation, you start up the application and choose the serial port that your badge is connected to (if it isn't auto detected), and you can start opening and editing the python files.

When Thonny is connected to the badge, you will have access to the REPL in a terminal (when the main code isn't running), and you can both copy your code over to the badge and run it after a reset, or you can simply run the code you have open in Thonny directly, without saving it to the badge.

If you are testing out different things, simply opening a file and running it on the badge is a quick way to experiment. If you only want to try out a single command, runnig it in the REPL is another very quick way to get started and test stuff.

## VSCode

After [installing VSCode](https://code.visualstudio.com/Download), you need to install the [MicroPico extension](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) and that is easiest done via the extension manager inside VSCode. Simply search for "MicroPico", install the extension and probably also the recommended additional extensions.

When you have the extension installed, you can create a new project (open a new folder), and run ```> MicroPico > Configure Project command``` via ```Ctrl+Shift+P``` (or the equivalent on your platform). This will setup the project as a MicroPico project and add a ```.vscode``` folder, with a bit of configuration.

Inside this hidden folder is some project settings and a link to stub files used for IntelliSense and code completion. This is for a regular Raspberry Pi Pico and will get you most of the way, but if you also want code completion for the display driver used on the badge (GC9A01), you can add the [Vectorscope folder](Vectorscope/) and it's content to this ```.vscode``` folder next to the ```Pico-W-Stub``` folder either by copying in the folder or by creating a symlink to the folder in this repository, if you have it checked out. To have MicroPico use these stubs edit the ```settings.json``` to also include this folder:

```json
{
    "python.linting.enabled": true,
    "python.languageServer": "Pylance",
    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingModuleSource": "none"
    },
    "python.analysis.typeshedPaths": [
        ".vscode/Pico-W-Stub",
        ".vscode/Vectorscope",
    ],
    "python.analysis.extraPaths": [
        ".vscode/Pico-W-Stub",
        ".vscode/Vectorscope",
    ],
    "micropico.syncFolder": "",
    "micropico.openOnStart": true
}
```

The new lines are line 10 and line 14, but remember to also add a comma after the preceding lines, to keep the json syntax valid.

## mpremote

The official [documentation for mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) has info on how to install and also detailed instructions for all the features.

It's really not that long a read, but the TLDR is here:

Install via ```pip install --user mpremote``` and then you can invoke the program with ```mpremote```

Run file on the badge

```
mpremote run file.py
```

Copy file from current folder to the badge

```
mpremote cp file.py :
```

Copy file from the badge to current folder

```
mpremote cp :main.py .
```

Mount current folder on the badge

```
mpremote mount .
```