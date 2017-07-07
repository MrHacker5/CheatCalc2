# CheatCalc 2.0
[If the first time ya didn't succeed...](https://github.com/MrHacker5/CheatCalc)

## Features
With this smart calculator you can:  

* solve linear algebra stuff with the help of some macros (ex: eigenSys(m) -> find all eigenvalues and eigenvectors)
* browse input history and use autocompletion
* search previously saved notes by title and tags

## How to build one: Requirements
* Raspberry Pi zero (wireless)
* if you have the rpi zero non wireless you need also a wifi dongle and an OTG adapter
* a calculator with buttons sensors on a PCB (if the sensors are on a plastic sheet, they make too much resistance and the rpi cannot register high signals)
* a graphic LCD (st7920)
* a step-up 3.7V->5V converter
* a Li-Po/Li-ion battery (3.7V)
* a Li-Po battery charger (5->3.7V)
* a multiplexer/demultipllexer 16 to 4
* soldering equipment
* cable-making equipment (ribbon cables, male + female dupont connectors, plastic caps, crimper)
* (angled) male headers
* a 2 state switch
* super glue (cyanoacrylate)
* Kapton (heat resistant) and electrical tape
* a 3D printer to print the calculator case

## Instructions
### Wiring
Extract the pcb from the calculator, desolder the battery holder and isolate the integrated chip on the PCB with a cutter or x-acto knife.  
Follow the circuit paths and map the button layout. It should be equivalent to a grid 4xN (N changes depending of the number of buttons, usually 12-15).  
Connect the PCB pads (if there aren't any, scrape the soldering mask over the circuit paths) corresponding to the paths of the larger side of the grid, to the multiplexer.  
Connect the remaining 4 paths and the input of the multiplexer to the Raspberry Pi. The signal pin of the multiplexer must be grounded.  
Connect the LCD as shown here:  
| LCD pin |  Rpi pin  |  
|  :---:  |   :---:   |  
|   RS    | 26 (CS0)  |  
|   RW    | 19 (MOSI) |  
|    E    | 11 (CLK)  |  
|   PSB   |    GND    |  
Please refer to https://github.com/JMW95/pyST7920.  
Connect the Raspberry Pi to the step-up which in turn is connected to the battery (with a switch on the VCC line).  
  
Use the Kapton tape and the electrical tape to isolate the components.  
Print the stl files in the folder `3d files`.

### Installation
You need to use the official distro Raspbian on the Raspberry Pi (this program uses Wolfram Mathematica).  
Install `python3, python-dev, python-rpi.gpio`. Then with pip3 install `pypng`.  
Enable SPI interface with `raspi-config`.  
Clone this repo in the folder `/home/pi/CheatCalc2/`.  
(Optional: download and setup [rclone](https://rclone.org/) to transfer the files from the cloud to the Raspberry.)  
In the file `CheatCalc2/key-layout.txt`:  

* modify the input and output pins according to your wiring
* modify the key function relative to each combination of input-output

Append to `/etc/rc.local` (remember the '&'):  
```sh /home/pi/Cheatcalc2/bootstrap.sh &```  

## Enjoy
Save your own notes in the file `CheatCalc2/notes.txt` and your macros in the file `CheatCalc2/macros.txt`.

## Gallery
![front](/front.jpg?raw=true)
![inside1](/inside1.jpg?raw=true)
![inside2](/inside2.jpg?raw=true)
