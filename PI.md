# NowPlaying Pi

Fork of [jasontate/raspberry-pi-now-playing](https://github.com/jasontate/raspberry-pi-now-playing)
(Last.fm "now playing" page, shown full-screen on a small square display).
Upstream is the `upstream` remote; this fork is `origin`. The Pi was originally set up
by cloning upstream into `/var/www/html` and deleting `.git`, so the Pi itself is not a git checkout.

## Device

| | |
|---|---|
| Hostname | `nowplaying` (`nowplaying.local`) |
| Address | 192.168.0.52 on `wlan0` (eth0 unused) |
| Hardware | Raspberry Pi 3 Model B Rev 1.2 |
| Display | Pimoroni Hyperpixel 4.0 Square (720x720), `dtoverlay=vc4-kms-dpi-hyperpixel4sq` |
| OS | Debian 13 (trixie), kernel 6.12.47+rpt-rpi-v8, 64-bit |
| Login | user `pi`, SSH key `~/.ssh/id_ed25519_nowplaying`, host alias `nowplaying` |
| Sudo | `pi` has passwordless sudo |
| Remote access | Raspberry Pi Connect enabled (signed in) |
| Stack | Apache 2 + PHP 8.4 (curl, mbstring), Chromium 141, labwc (Wayland), lightdm, unclutter |

## How it works

1. Apache serves `/var/www/html` (this repo's `index.php`, `style.min.css`, `artwork-placeholder.png`).
2. `index.php` polls the Last.fm API (`LASTFM_API_KEY`, `LASTFM_USER`) for recent tracks.
3. labwc autostart (`pi/labwc/autostart`) launches Chromium in kiosk mode on `http://nowplaying.local`.
4. `hyperpixel-mqtt.service` runs `pi/hyperpixel_mqtt_control_final.py`, which subscribes to
   MQTT topic `nowplaying/backlight` on the broker at 192.168.0.4:1883 to switch the display backlight.

## Changes from upstream

- `index.php`: CSS rule hiding the mouse cursor; Last.fm key/user set on the Pi (placeholders here).
- `style.min.css`: `cursor:none` on `body`.
- Extra Pi files under `pi/` (not part of upstream).

## Secrets (not in git)

- `LASTFM_API_KEY` / `LASTFM_USER` in `/var/www/html/index.php` on the Pi.
- `MQTT_USERNAME` / `MQTT_PASSWORD` in `/home/pi/hyperpixel_mqtt_control_final.py` on the Pi.

Repo copies hold placeholders. Don't overwrite the Pi files blindly: fill the values in after deploying.

## Deploy / file map

| Repo | On the Pi |
|---|---|
| `index.php`, `style.min.css`, `style.css`, `artwork-placeholder.png` | `/var/www/html/` |
| `pi/hyperpixel_mqtt_control_final.py` | `/home/pi/hyperpixel_mqtt_control_final.py` |
| `pi/systemd/hyperpixel-mqtt.service` | `/etc/systemd/system/hyperpixel-mqtt.service` |
| `pi/labwc/*` | `/home/pi/.config/labwc/` |
| `pi/config.txt` | `/boot/firmware/config.txt` (reference copy, active lines only) |

## Pulling upstream updates

```bash
git fetch upstream && git merge upstream/main
```

## Rebuild notes

Install `apache2 php php8.4-curl php8.4-mbstring python3-paho-mqtt unclutter chromium`, enable the
Hyperpixel overlay in `config.txt`, copy the files above, then
`sudo systemctl enable --now hyperpixel-mqtt.service`.
