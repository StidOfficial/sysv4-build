# svr4-build

Automated install of UNIX System V Release 4

Run `./download.sh` and `./install.py`

## Use serial port

```
echo "s1:respawn:/etc/getty tty0 19200" >> /etc/inittab
init q
```