# Little Unicorn

A new kind of baby monitor using Raspberry Pi and the beautiful [Unicorn HAT HD from Pimoroni](https://shop.pimoroni.com/products/unicorn-hat-hd). It provides a way to visualise the noises your little unicorns are making, without the stress of hearing them screaming.

## Requirements
### Hardware
- 2 x Raspberry Pi (with wireless already setup). One is the listener (server), one is the display (client)
- 1 x USB mic
- Unicorn HAT HD

### Software
- Raspbian is recommended (but greater than Wheezy for Unicorn HAT HD)
- Git
- Python 3

After downloading Little Unicorn into `littleunicorn`, all required packages can be installed with installed with:

```bash
sudo pip3 install -r littleunicorn/requirements.pip
```

## Running

On your Raspberry Pi with the microphone, run the server code e.g.

```bash
cd littleunicorn
python3 server.py
```

then on your Raspberry Pi with the Unicorn HAT HD, run the client code. You will need to pass either the IP address or the machine name of your server e.g.

```bash
cd littleunicorn
python3 client.py 192.168.1.10
```

You will probably want to run these 'headless' i.e. without a monitor attached or an active SSH session. You can use `nohup` for that e.g.

```bash
nohup python3 client.py 192.168.1.10 &
```

#### Running at start up
You can run either of these when your Pi boots up by adding the following to your crontab `crontab -e`, e.g.

```bash
@reboot python3 /home/pi/littleunicorn/server.py >> /home/pi/unicorn.log 2>&1
```
