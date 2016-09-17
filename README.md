# mailnag-messagingmenu-plugin
Plugin that integrates [Mailnag](https://github.com/pulb/mailnag) in the MessagingMenu indicator.
The MessagingMenu indicator is currently available for the following desktops:
 - Ubuntu Unity
 - Elementary Pantheon
 - XFCE
 - GNOME 3

## Installation

### Ubuntu PPA
This plugin is available in the official [Ubuntu PPA](https://launchpad.net/~pulb/+archive/mailnag).  
Issue the following commands in a terminal to enable the PPA and install the plugin.  

    sudo add-apt-repository ppa:pulb/mailnag
    sudo apt-get update
    sudo apt-get install mailnag-messagingmenu-plugin

### Generic Tarballs
Sourcecode releases are available [here](https://github.com/pulb/mailnag-messaging-plugin/releases).  
To install the plugin type `sudo ./setup.py install --prefix=/usr --install-layout=deb` in a terminal.
That's it. Now fire up `mailnag-config` and enable the plugin.  

###### Requirements
* mailnag >= 1.0.0
* gir1.2-messagingmenu-1.0

## Screenshots
![Screenshot](https://raw.github.com/pulb/mailnag-messagingmenu-plugin/docs/docs/screenshot.png)
