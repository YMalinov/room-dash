# room-dash

A simple, full-screen-running app, showing weather data readings from the home-sensors project, a clock (with precision up to seconds), current date and current date of week. It's meant to run on Raspberries and supports routining: as in, you're able to pick at which times and days of the week the monitor showing the app would turn on and off. It's also meant to run as a user-space systemd service, turning on at Raspberry boot up. The weather data readings get cached for 14 minutes at a time, such that we don't send unneccessary requests to the AppEngine project, which runs home-sensors, and in doing so, exceed the free quota there. Currently, the app is composed of two threads: one main one, dealing with the UI, clock and date; as well as a worker thread, dealing with the GET requests, directed at home-sensors. The routine is able to get overridden: if the app detects that the monitor has been turned on from outside of the app itself, programmatically: the HTTP server from the rouser-pi project exposes routes able to do so.
<br><br>
Screenshot:<br>
![screenshot](https://github.com/hatrox/room-dash/raw/master/screenshot.png)
<br>