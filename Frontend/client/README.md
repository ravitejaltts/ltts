
# Client scripts:
`npm start` starts development web server

`npm run build` creates production build

# Deploying to HMI
1) Find HMI ip address
   1) Go to Settings/System (tap title 10 times)/Functional Control Panel/System
   2) You should be able to use either IP Address
2) ssh roo@[ip]
   1) `cd /opt/smartrv/smartrv-frontend`
   2) `mount -o remount,rw /` makes the drive writeable
   3) `rm -rf *` clears all current site content
3) upload build
   1) From your local Frontend/client directory
   2) `npm run build` builds the server-intent code
   3) `scp -r build/* root@[ip]:/opt/smartrv/smartrv-frontend/` upload to HMI
4) Reload the browser
   1) By holding on the WGO logo on the home page
   2) From the ssh, restart the HMI if the page reload trick doesn't work
      1) `systemctl restart smartrv-kiosk`
   3) clear cache if needed:
      1) `rm -rf /.cache/qt-kiosk-browser`
      2) `rm -rf /root/.cache/qt-kiosk-browser`
      3) `rm -rf /home/weston/.cache/qt-kiosk-browser`
