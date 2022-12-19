# svr4-build

Automated install of UNIX System V Release 4

Run `./download.sh` and `./install.py`

## Add user

```
adduser user user 1000 /home/user
```

Use TERM=`AT386-M`

## Use serial port

```
echo "s1:12345:respawn:/etc/getty tty00 9600 none LDISC0" >> /etc/inittab
init q

sed "s/console/tty00/g" /etc/default/login > /etc/default/login.bak
mv /etc/default/login.bak /etc/default/login
```