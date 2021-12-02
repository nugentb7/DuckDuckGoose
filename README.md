# Duck Duck Goose

This repository houses all files for our final project.

## Apps
- [Web App](https://duck-duck-goose.herokuapp.com)
- [d3.js Observable workbook](https://observablehq.com/d/377e9b6eed0ff437)

*Note: for the d3.js visual, you must check the locations in order for the errors to clear*

## Team members 

- [Brendan Nugent](https://github.com/nugentb7)
- [Connor Hornibrook](https://github.com/cfh294)
- [Andy Cuccinello](https://github.com/Djphoenix719)
- [Christene Harris](#)
- [Christina Bannon](#)
- [Lixaris Martini](#)

## Initializing the Database

Clear out existing data (don't do this if the database is already empty):

```bash
./scripts/db-init.py -d
```

Run the initializer and load the data:

```bash
./scripts/db-init.py
./scripts/db-load.py
```

The ```sqlite``` database is located at ```./scripts/waterways.db```.
