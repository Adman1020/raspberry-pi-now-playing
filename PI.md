# NowPlaying Pi

Fork of [jasontate/raspberry-pi-now-playing](https://github.com/jasontate/raspberry-pi-now-playing)
(Last.fm "now playing" page, shown full-screen on a small square display).
Upstream is the `upstream` remote; this fork is `origin`. The Pi was originally set up
by cloning upstream into `/var/www/html` and deleting `.git`; it has since been re-initialised as a checkout of this fork.

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
4. `hyperpixel-mqtt.service` runs `pi/hyperpixel_mqtt_control_final.py`, which switches the display
   backlight on MQTT `nowplaying/backlight` messages. See "Screen power control" below.

## Screen power control (presence + playing)

The screen is meant to be on only when someone is in the room **and** music is playing.
The decision is made by **Home Assistant**, not by anything on this Pi.

**Verified (read from the Pi):**

- Home Assistant OS runs at `192.168.0.4`, and the MQTT broker is on the same host (port 1883, username/password auth).
- `hyperpixel-mqtt.service` runs `pi/hyperpixel_mqtt_control_final.py` as user `pi`. It subscribes to
  topic **`nowplaying/backlight`** and accepts payload `on` or `off` (case-insensitive; anything else is ignored).
- On `on`/`off` it writes `1`/`0` to `/sys/class/backlight/backlight/brightness` using `sudo tee`
  (works because `pi` has passwordless sudo).
- Only the **backlight** is switched. Chromium keeps running, so the page stays loaded and updates
  while the screen is dark.

**Not verified (inferred, Home Assistant config was not read):**

- Something in Home Assistant (presumably an automation) publishes `on`/`off` to `nowplaying/backlight`
  when the room's presence sensor and the Spotify/media player state change. Which sensor and which
  media player entity it uses is not recorded here.
- To find it: in Home Assistant, Settings > Automations, look for an automation with an MQTT publish
  action on `nowplaying/backlight`. Once found, add the entity names and conditions to this section.

Manual test, from any machine with `mosquitto_pub`:

```bash
mosquitto_pub -h 192.168.0.4 -u <user> -P <password> -t nowplaying/backlight -m off   # or: on
```

## Changes from upstream

- `index.php`: CSS rule hiding the mouse cursor; Last.fm key/user loaded from `config.local.php` instead of hardcoded.
- `style.min.css`: `cursor:none` on `body`.
- Extra Pi files under `pi/` (not part of upstream).

## Secrets (not in git)

- `LASTFM_API_KEY` / `LASTFM_USER` in `/var/www/html/config.local.php` on the Pi (gitignored; template in `config.local.php.example`).
- `MQTT_USERNAME` / `MQTT_PASSWORD` in `/home/pi/hyperpixel_mqtt_control_final.py` on the Pi.

The repo holds placeholders only. `/var/www/html` on the Pi is a git checkout of this fork, so deploying is `cd /var/www/html && git pull`.

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
