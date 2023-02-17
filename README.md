# IQR-pan-tilt-python

Only tested on ubuntu.

```bash

# clone
git clone https://github.com/powei-lin/IQR-pan-tilt-python.git iqr_pt_python
cd iqr_pt_python

# add usb rules, need to plug in use after this step
sudo cp data/56-pan-tilt.rules /etc/udev/rules.d

# install
pip install .

# command line tool
iqr_pan_tilt_tool 40 50 30

```