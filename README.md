# Geant4-TAU-SAT
## Compile
Create a new `build` folder: `mkdir build`\
Change dir to new folder: `cd build`\
Run: \
`cmake -DGeant4_DIR=/cvmfs/geant4.cern.ch/geant4/10.5/x86_64-slc6-gcc63-opt-MT/lib64/Geant4-10.5.0 ../build`\
in `build` folder, where `-DGeant4_DIR` is the path to Geant4 installation folder in current OS\
In the new `build` folder, run: \
`make`
## Run
Run `./Sim` for UI simulation run.\
Run `./Sim *input.txt*` to run batch.

To run using our script:\
`make_data.py` would create a batch of current run parameters.\
`run_data.py`/`run_data_threads.py` would run the entire batch:
* `run_data.py --run` would run the batch and save Geant4 results to a file
* `run_data.py --parse` would gather all previous run data to a single `csv` file for data analysis.

### `make_data.py`
run command:
`python make_data.py [save_path] [input_json_path]`
* `save_path` - where to create the directory containing each simulation case. input `.` for current run directory.
* `input_json_path` - path to json file containing simulation cases to create. for example: (`example.json`)
    
    ``` json
    {
    "energies": [
        0.5, 0.64, 0.82, 1.06, 1.35, 1.74, 2.23, 2.86, 3.67, 4.71, 6.04, 7.74, 9.94, 12.75, 16.35, 20.98, 26.91, 34.52, 44.29, 56.82, 72.89, 93.51, 119.96, 153.89, 197.42, 253.27, 324.91, 416.82, 534.72, 685.98, 880.03, 1128.97, 1448.33, 1858.02, 2383.61, 3057.88, 3922.87, 5032.56, 6456.14, 8282.42, 10625.31, 13630.94, 17486.79, 22433.36, 28779.19, 36920.1, 47363.87, 60761.91, 77949.93, 100000.0
    ],
    "positions": [
        [
            0, 0, -4
        ]
    ],
    "directions": [
        [
            0, 0, 1
        ]
    ],
    "particles": [
        "mu+", "e-", "proton", "mu-", "e+", "ion"
    ],
    "ions": [
        [
            2, 4, 2
        ],
        [
            6, 12, 6
        ],
        [
            8, 16, 8
        ],
        [
            26, 52, 26
        ]
    ],
    "beamOn": 10
    }
    ```
    * `energies` - initial energy of the particle.
    * `positions` - position of the particle gun.
    * `directions` - direction of the particle gun.
    * `particles` - types of particles to simulate.
    * `ions` - types of ion to simulate (relevant if `ion` is included in `particles`)
    * `beamOn` - how many simulations of each case.
    
Using the `example.json` and the current directory for output:\
`python make_data.py . ./example.json`

### `run_data.py` / `run_data_threads.py`
We recommend using `run_data_threads.py` to utilize multi-threaded runs.\

Run command:
`python run_data_threads.py -j[number of threads] -dir[run dir] -parse[parsing data] -run[running simulations]`

* `run` - specifiying this execution is to run Geant4 simulation. (cannot be enabled with `parse`)
* `parse` - specifiying this execution is to gather the data to a unified `csv` file. (cannot be enabled with `run`)
* `dir` - specify the dir containing our test cases. (should be equivalent to the `save_path` of `make_data.py`)
* `j` - specify the number of threads to run.