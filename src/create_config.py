import configparser



config = configparser.ConfigParser()

config['pyserial'] = {

    'Port': '/dev/ttyUSB0',
    'Baudrate': '115200',
    'Timeout': '1'
}

config['jailbreak'] = {

    'Message':'PRISON BREAK ALERT! ESTABLISH CHECKPOINTS!',

    'Console_txt':'JailBreak Detection\nFor educational use only\nThe creators held no liabilities' \
                  ' for any damages and problem due to miss use of the app.\nDevelopers: \n',

    'Occupied':'Motion Detected!',

    'Unoccupied':'Unoccupied      ', #observer the spaces
}

config['cv'] = {
    'Min-area':'50'
}
with open('config.ini', 'w+') as configfile:
    config.write(configfile)
