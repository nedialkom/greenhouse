# greenhouse
1. Setup the Pi4 hardware:
   Plug the GrovePi+ in the slot
   Connect the humidity sensor to A0 and the relay to D4 ports
2. setup of Pi4 software
   python3 -m pip install awsiotsdk
   curl -kL dexterindustries.com/update_grovepi | bash
   sudo reboot
   cd ~/Dexter/GrovePi
   sudo git fetch origin
   sudo git reset --hard
   sudo git merge origin/master
   cd /home/pi/Desktop/GrovePi/Firmware
   sudo chmod +x firmware_update.sh
   sudo ./firmware_update.sh
   cd ~
   git clone https://github.com/nedialkom/greenhouse.git
   cd greenhouse/Pi4

   