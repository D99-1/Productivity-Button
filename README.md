# Productivity Button
This is a button.

That pretty much explains the whole project but let me tell you a little more. This button was designed to be a simple way to start and stop the [Toggl](https://toggl.com) Time Tracker, but while making it, I thought why not give it a few more purposes like turning on desk lights and triggering Alexa routines.

As of now, since I don't have smart lights, this button only triggers Toggl, but if you do have smart devices set up then the routines you can setup are endless.
# How It Works
## Wiring
This consists of a Pico W hooked up to a button on Pin 2, and an LED on pin 11. That's simply it, there's nothing more to it.
## Function
The Pico sends a GET request to the Toggl API every 10 seconds to check if there is a running session, if there is, the LED turns on, if not, it turns off. When the button is pressed, a web request is sent to check the status and then another web request is sent to turn time tracking on or off accordingly.
## Case
This case was 3D printed to fit inside the cupholder slot of the IKEA Fredde Desk however I reccomend you stay far away from this model. The model actually broke partially after printing however I somehow managed to salvage it and it fit together.
# Images
![IMG_20250130_180617740](https://github.com/user-attachments/assets/2757a61c-279f-4706-8fa2-2b52e58ddbf4)
![IMG_20250130_180220894](https://github.com/user-attachments/assets/cd9e5f38-11a1-40f6-b038-f3b0c100aea1)
![IMG_20250130_180312014](https://github.com/user-attachments/assets/46165232-9a08-4356-92b8-bdf461cac27e)
