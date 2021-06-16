# FAKEOBS

## Installation

Steps to install the `fakeobs` task into `casa`

 1. Clone the git repository into a directory of your choice
 (e.g., $HOME/.casa/NordicTools)

``` shell
cd $HOME/.casa/NordicTools
git clone <repository url>
cd fakeobs
buildmytasks --module fakeobs checkres.xml
```
 2. Inside `casa` add the folder to your `PYTHONPATH`:

``` python
CASA <1>: sys.path.insert(0, <path to fakeobs folder>)
CASA <2>: from fakeobs.gotasks.fakeobs import fakeobs
CASA <3>: inp(fakeobs)

```

That's it! Enjoy!
